# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Archive system for the Ministry of Culture of Uzbekistan (Madaniyat vazirligi Arxiv tizimi). Documents organized by year and category, with dynamic fields per category. Each category belongs to one year. When creating a new year, categories can be imported (copied) from an existing year. A second, separate subdomain (`music_school_*`) tracks music-school diplomas with its own role-scoped access.

## Tech Stack

- **Backend**: Python 3.13 + FastAPI + SQLAlchemy (async) + Alembic
- **Frontend**: Nuxt 4 + @nuxt/ui v4 + Tailwind CSS v4 + Zod
- **Database**: PostgreSQL 16 (prod + dev default); SQLite (legacy dev only)
- **Search**: Elasticsearch 8.15 with ICU plugin (custom `docker/elasticsearch` image)
- **Queue / OCR**: Redis 7 + `arq` worker + Tesseract + PyMuPDF + pdf2image
- **Auth**: JWT (username/password), bcrypt for hashing
- **Package managers**: `uv` (Python), `npm` (frontend)

![1778683638837](image/CLAUDE/1778683638837.png)

## Commands

Everything is wired through the root `Makefile`:

```sh
make install          # uv venv + uv pip install -e (backend), npm install (frontend)
make dev              # open backend + frontend in two Windows Terminal tabs (wt)
make backend          # uv run uvicorn src.api.main:app --reload --host 0.0.0.0
make frontend         # npx nuxi dev --host 0.0.0.0
make worker           # uv run arq src.infrastructure.jobs.worker.WorkerSettings
make migrate          # alembic upgrade head
make migration m="add foo table"   # autogenerate revision
```

Docker compose profiles (see [README.md](README.md)):

```sh
docker compose up -d                        # default: db + redis + elasticsearch only
docker compose --profile app up -d          # + backend + frontend (full stack)
docker compose --profile tools up -d kibana # Kibana at :5601
docker compose down -v                      # wipe pgdata/redisdata/esdata/uploads
```

Reindexing / one-off scripts (run with `uv run python -m ...` from `backend/`):

```sh
python -m scripts.reindex                   # enqueue every doc into the outbox
python -m scripts.reindex --year 2024
python -m scripts.reindex --since 2024-01-01
python -m scripts.reindex --dry-run
python -m scripts.ocr_backfill              # backfill OCR for legacy documents
python -m scripts.migrate_sqlite_to_postgres
python create_admin.py                      # bootstrap an admin user
python seed_music_schools.py                # seed music-school reference data
python import_document_types.py
python import_reference_data.py
```

Health check: `GET /api/health` → 200 only when Postgres, Elasticsearch, and Redis are all reachable; 503 with per-dep status otherwise.

No test runner is wired up — there is no `pytest`/`vitest` invocation in this repo yet. Verify changes by running the stack and exercising endpoints.

## Architecture

Backend follows DDD (Domain-Driven Design):

```
backend/src/
  domain/         # Entities, value objects, repository interfaces (no external deps)
                  # Aggregates: user, year, category, document, person, department,
                  # archive_folder, document_type, music_school, music_school_document,
                  # music_school_specialty
  application/    # Commands, queries, handlers per aggregate (depends on domain only)
  infrastructure/
    persistence/  # SQLAlchemy models, mappers, repositories, database session
    auth/         # JWT + bcrypt password service
    file_storage/ # local_storage.FileStorageService (writes to UPLOAD_DIR)
    search/       # es_client, index_template + music_index_template (versioned aliases),
                  # document_indexer + music_document_indexer, query_builder
    ocr/          # ocr_service.extract_text (PyMuPDF fast path + Tesseract fallback)
    jobs/         # arq_pool (FastAPI-side enqueue), worker.WorkerSettings (drain + OCR)
  api/            # FastAPI routes, Pydantic schemas, middleware (entry point)
    routes/       # One module per aggregate + search_routes, reference_routes
    middleware/   # auth: get_current_user, require_admin, require_music_school_or_admin
backend/scripts/  # reindex, ocr_backfill, migrate_sqlite_to_postgres
backend/data/     # Source JSON for reference imports (Murojaat turi, Hujjat shakli, …)
```

Frontend:

```
frontend/app/
  layouts/        # auth.vue (login), dashboard.vue (sidebar + user menu)
  pages/          # File-based routing (see Route Map below)
  components/     # PagePanel, EmptyState, DatePicker, FieldModal, MusicSchool*, document/*
  composables/    # useAuth, useDocuments, useSearch, useMusicSchool, usePersons,
                  # useDepartments, useArchiveFolders, useDocumentTypes, useReferences
  middleware/     # auth.global.ts (route guard)
  utils/          # api.ts (JWT fetch wrapper), labels.ts
  types/          # TypeScript interfaces
```

## Search + OCR Pipeline (Phase 5/6)

There are **two** Elasticsearch indices, each behind a versioned alias:

- `documents` alias → `documents-v1` (general documents) — [src/infrastructure/search/index_template.py](backend/src/infrastructure/search/index_template.py)
- `music_school_documents` alias → `music_school_documents-v1` — [music_index_template.py](backend/src/infrastructure/search/music_index_template.py)

Both use a custom `uz_multi` analyzer (ICU tokenizer + folding + Russian stemmer) so a single query matches across Uzbek Latin, Uzbek Cyrillic, and Russian. Titles get an extra `uz_autocomplete` edge-ngram field. **Reindex without downtime by building `*-v2`, populating it, then swapping the alias** — never write directly to the concrete index.

Writes never touch Elasticsearch synchronously. The flow is:

1. Repository commits the Postgres write **and** appends a `SearchIndexJobModel` row (`op="index" | "delete"`, `entity_type="general" | "music_school"`) — this is the outbox pattern.
2. The `arq` worker's `drain_search_outbox` cron runs every 2 seconds, pulls up to `DRAIN_BATCH_SIZE=100` rows, and dispatches to the right indexer. Failures break the batch but don't drop the row.
3. After a file upload, the route enqueues `ocr_extract(document_id, attachment_id?)`. The worker flips `ocr_status pending → processing → done/failed/skipped`, writes `extracted_text`, and re-emits an outbox row so the new text lands in ES.

`ocr_extract` handles general docs, music-school docs, and document attachments — it looks the target up by ID and infers the entity type. Failures are surfaced via `ocr_status` and never block the request.

OCR (`src/infrastructure/ocr/ocr_service.py`): PDF fast path uses PyMuPDF's embedded text layer; if fewer than `MIN_EMBEDDED_TEXT_CHARS = 100` characters come back, it falls through to `pdf2image` + Tesseract (`uzb+uzb_cyrl+rus+eng`, 300 DPI). Images go straight to Tesseract. `extract_text` is sync and CPU-bound — always `run_in_executor` it from async code (the worker already does).

The worker container ([backend/Dockerfile.worker](backend/Dockerfile.worker)) ships all four Tesseract language packs + `poppler-utils`. Native-dev workers need those installed locally.

## Roles & Access Control

`UserRole` (StrEnum): `admin`, `user`, `viewer`, `music_school`. Auth middleware:

- `get_current_user` — JWT decode + active-user check
- `require_admin` — admin only
- `require_music_school_or_admin` — gates the entire music-school subdomain

Music-school users see only their own school's documents — ownership is enforced by comparing `current_user.music_school_id` against `doc.music_school_id` in route handlers (e.g. `_check_ownership` in `music_school_document_routes.py`).

## Key Gotchas

- **Pydantic schemas**: Do NOT use `from __future__ import annotations` — breaks Pydantic type evaluation at runtime.
- **UTable (TanStack Table v3)**: Columns use `accessorKey`/`header` (not `key`/`label`). Empty-header columns need explicit `id`. Cell slot data accessed via `row.original.*` (not `row.*`).
- **find_by_year()**: The `year_id` parameter is the year VALUE (e.g. 2020), not the DB primary key. Repository joins `YearModel` to match by `YearModel.value`.
- **GUID + JSONType**: Models use custom `GUID` (native UUID on Postgres, CHAR(36) elsewhere) and `JSONType` (JSONB on Postgres, JSON elsewhere). Alembic autogenerate writes `GUID` as `src.infrastructure...GUID(length=36)` — manually replace with `sa.String(length=36)` in migration files.
- **No passlib**: Incompatible with newer bcrypt. Using `bcrypt` library directly via `src/infrastructure/auth/password_service.py`. (`passlib` is still listed in `pyproject.toml`; do not import it.)
- **CORS origins**: Configured via `CORS_ORIGINS` env (comma-separated) → `src/infrastructure/config.py`. Default includes `http://localhost:3000` and `http://192.168.20.247:3000`. Update env/compose when deploying or changing frontend port.
- **Color mode**: Forced to `light` in `nuxt.config.ts` (`colorMode.preference` and `fallback`).
- **Search writes via outbox only**: Never call the ES client from request handlers. Repository commits the row + outbox in the same transaction; the worker drains it. If ES is down, writes still succeed and search catches up when the worker drains backlog.
- **Both index templates on startup**: `main.py` lifespan calls `ensure_general_index` AND `ensure_music_index`. The worker startup does the same. A failure is logged-not-fatal so non-search endpoints stay up.
- **Reference JSON paths**: `regions.json` and `districts.json` live at `backend/src/infrastructure/persistence/data/` and are loaded with `encoding="utf-8-sig"` (BOM-tolerant) and cached in module globals. Other reference seeds (`Hujjat shakli.json`, `Murojaat turi.json`, etc.) live at `backend/data/` and are loaded by the `import_*` scripts.
- **OCR target lookup**: `ocr_extract` first tries `DocumentModel`, falls back to `MusicSchoolDocumentModel` — adding a third indexable entity means updating this dispatch.

## Domain Patterns

- **Category-Year relationship**: Each category has a single `year_id` FK. `import_from_year_id` on year creation copies categories with all fields as new records.
- **Default field templates**: `default_fields` table stores admin-managed templates. Auto-copied as initial category fields when creating a category. Admin page at `/admin/default-fields`.
- **Copy category**: `POST /api/categories/{id}/copy` with `{ target_year_id }` duplicates a category (name/code/fields) into the target year.
- **Dynamic fields (EAV)**: `category_fields` defines field schemas per category, `document_field_values` stores per-document data. Common document fields (title, date, etc.) are real columns and are also denormalized into the ES `field_values` nested array for search.
- **File upload**: Two-step — create document first, then `POST /api/documents/{id}/file` with FormData. Download uses authenticated `fetch()` + blob URL (JWT required). Upload routes also enqueue `ocr_extract` via the arq pool.
- **Attachments**: General documents support multiple secondary files via `document_attachments`. Attachments are indexed as a nested `attachments` field in ES, and their highlights are flattened out of `inner_hits` by the search route before responding.
- **PDF viewer**: Uses `pdfjs-dist` with authenticated fetch (blob URL) since file API requires JWT.
- **DatePicker**: `UInputDate` + `UPopover` + `UCalendar` from Nuxt UI v4. Converts between `YYYY-MM-DD` string (backend) and `CalendarDate` (frontend).
- **Person + tenures**: `Person` aggregate owns a list of `Tenure(position, start_date, end_date)`. `GET /api/persons/active?date=YYYY-MM-DD` returns persons whose tenure window covers that date (used to attribute documents to who was in office). Admin-managed at `/admin/persons`.
- **Archive folders**: A separate physical-storage hierarchy (index code + title) that documents can be filed into. Browse at `/archive-folders`; manage via `/api/archive-folders`.
- **Music school subdomain**: Mirrors the main flow but the document entity is diploma-shaped (student_full_name, specialty, diploma serial/number, given_date, passport_series/number, PINFL). Separate ES index, separate routes, scoped by user's `music_school_id`. Diplomas reference reusable specialties (`music_school_specialties` table).

## Configuration

`src/infrastructure/config.py` (`pydantic-settings`, reads `backend/.env`):

| Setting | Default |
|---|---|
| `database_url` | `postgresql+asyncpg://postgres:postgres@localhost:5432/arxiv_db` |
| `redis_url` | `redis://localhost:6379/0` |
| `elasticsearch_url` | `http://localhost:9200` |
| `secret_key` | dev placeholder (min 32 chars in prod) |
| `access_token_expire_minutes` | 480 |
| `upload_dir` | `uploads` |
| `cors_origins` | `http://localhost:3000,http://192.168.20.247:3000` |

Frontend reads `NUXT_PUBLIC_API_BASE` (default `http://localhost:8000` in `nuxt.config.ts`).

## Route Map

```
/login                                                # Username/password
/archive                                              # Year grid
/archive/:year                                        # Documents table + category/date filter
/archive/:year/:categoryId/:id                        # Document detail (PDF preview)
/archive/:year/:categoryId/:id/edit
/archive/search                                       # Full-text search UI

/archive-folders                                      # Browse + filter folders
/music-school-archive                                 # Diploma list (scoped to user's school)
/music-school-archive/create
/music-school-archive/:id
/music-school-specialties                             # Specialty picker UI

/admin/users                                          # admin only
/admin/years                                          # + import categories
/admin/categories                                     # + copy
/admin/categories/:id/fields
/admin/default-fields
/admin/persons                                        # CRUD + tenures
/admin/departments
/admin/music-schools
```

## API Endpoints

```
GET    /api/health                                    # postgres + es + redis combined status

POST   /api/auth/login
GET    /api/auth/me

GET|POST        /api/users
GET|PUT|DELETE  /api/users/:id
PUT             /api/users/:id/password

GET|POST        /api/years                            # GET: ?active_only=true
PUT|DELETE      /api/years/:id
                                                       # POST body: { value, is_active, import_from_year_id? }

GET|POST        /api/categories
PUT|DELETE      /api/categories/:id
POST            /api/categories/:id/copy              # { target_year_id }
GET             /api/years/:yearValue/categories

GET|POST        /api/categories/:id/fields
PUT|DELETE      /api/categories/:id/fields/:fieldId

GET|POST        /api/default-fields
PUT|DELETE      /api/default-fields/:id

GET|POST        /api/documents                        # GET: ?year_id&category_id&search&date_from&date_to&field_filters&page&page_size
GET|PUT|DELETE  /api/documents/:id
POST            /api/documents/:id/file               # upload (FormData) — enqueues ocr_extract
GET             /api/documents/:id/file               # download (JWT required)

POST            /api/search                           # ES full-text + facets across general docs

GET|POST        /api/persons                          # GET: ?search=
GET|PUT|DELETE  /api/persons/:id
GET             /api/persons/active                   # ?date=YYYY-MM-DD

GET|POST        /api/departments
GET|PUT|DELETE  /api/departments/:id

GET|POST        /api/archive-folders
GET|PUT|DELETE  /api/archive-folders/:id

GET|POST        /api/document-types
GET|PUT|DELETE  /api/document-types/:id

# Reference / lookup tables
GET             /api/regions                          # ?type=LOCAL|ABROAD (JSON file backed)
GET             /api/districts
GET             /api/reception-places
GET             /api/appeal-types
GET             /api/retention-periods

# Music school subdomain (require_music_school_or_admin)
GET|POST        /api/music-schools                    # admin to create
GET|PUT|DELETE  /api/music-schools/:id

GET|POST        /api/music-school-specialties
GET|PUT|DELETE  /api/music-school-specialties/:id

GET|POST        /api/music-school-documents
GET|PUT|DELETE  /api/music-school-documents/:id
POST            /api/music-school-documents/:id/file
GET             /api/music-school-documents/:id/file
POST            /api/music-school-documents/search
```

## Theme

Primary color: `#043B87` (ministry blue) — defined as `madaniyat` in `app/assets/css/main.css` and set as `primary` in `app/app.config.ts`. All UI labels in Uzbek.
