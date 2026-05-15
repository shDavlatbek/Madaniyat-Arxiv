# Implementation Plan: Department → Archive Folder → Document Overhaul

## Overview

Three sequential feature slices that bring the archive closer to the reference site
(arxiv.gov.uz, see [image/CLAUDE/1778683638837.png](../image/CLAUDE/1778683638837.png)):

1. **Department (Bo'lim)** — new standalone aggregate with admin card-grid UI.
   **User model is NOT touched in this iteration.** Connecting users to departments
   is deferred to a future phase.
2. **Archive Folder (Yig'ma jild)** — new aggregate with `index_code, title,
   retention_period, start_date, end_date, document_count`.
3. **Document overhaul** — add `document_view` (incoming/outgoing/internal/appeal),
   link to archive folder, add `document_form`, `sender`, `language`,
   `related_document_number/date`, and render conditional fields per view in the form.

## Naming Convention

- **Backend column / Python identifier / API field / TypeScript type**: **English**
  (`department`, `archive_folder`, `document_view`, `related_document_number`, …).
- **Frontend visible label**: **Uzbek** (`Bo'lim`, `Yig'ma jild`, `Hujjat ko'rinishi`,
  `Aloqador hujjat raqami`, …).
- Map of identifier → label kept in `app/utils/labels.ts` (single source of truth so
  the Uzbek strings live in one place, not scattered through templates).

### Identifier ↔ Label table

| English identifier            | Uzbek label                  |
|-------------------------------|------------------------------|
| `department`                  | Bo'lim                       |
| `archive_folder`              | Yig'ma jild                  |
| `index_code`                  | Indeksi                      |
| `title`                       | Sarlavha                     |
| `retention_period`            | Saqlash muddati              |
| `retention_period: 3_years`   | 3 yil                        |
| `retention_period: 5_years`   | 5 yil                        |
| `retention_period: 10_years`  | 10 yil                       |
| `retention_period: 25_years`  | 25 yil                       |
| `retention_period: 50_years`  | 50 yil                       |
| `retention_period: 75_years`  | 75 yil                       |
| `retention_period: permanent` | Doimiy                       |
| `retention_period: epk`       | EPK                          |
| `start_date`                  | Boshlanish sanasi            |
| `end_date`                    | Tugash sanasi                |
| `document_count`              | Hujjatlar soni               |
| `document_view`               | Hujjat ko'rinishi            |
| `document_view: incoming`     | Kiruvchi hujjat              |
| `document_view: outgoing`     | Chiquvchi hujjat             |
| `document_view: internal`     | Ichki hujjat                 |
| `document_view: appeal`       | Murojaat                     |
| `document_form`               | Hujjat shakli                |
| `sender`                      | Kim tomonidan yuborilgan     |
| `language`                    | Tili                         |
| `related_document_number`     | Aloqador hujjat raqami       |
| `related_document_date`       | Aloqador hujjat sanasi       |
| `received_date`               | Qabul qilingan sana          |
| `origin_organization`         | Kelib chiqqan tashkilot      |
| `sent_date`                   | Yuborilgan sana              |
| `recipient_organization`      | Qabul qiluvchi tashkilot     |
| `applicant_full_name`         | Murojaatchi F.I.Sh.          |
| `applicant_phone`             | Murojaatchi telefoni         |

Out-of-scope for now (future phases): Statistika, Ro'yxatlar, Kelib tushganlar filter
view, Hujjat turlari taxonomy, Nomenklatura workflow states, User↔Department link.

## Architecture Decisions

- **DDD layout preserved.** Each new aggregate gets its own
  `domain/{name}/`, `application/{name}/`, mappers, repositories, schemas, routes —
  same shape as `person`.
- **User model untouched.** No `department_id`, no `jshshir`, no role-enum changes.
- **No category removal.** Existing `Category` ≈ "Nomenklatura" in current UI. We add
  new universal columns to `Document` (not via the EAV `category_fields`).
- **`Document.document_count` on archive folder** is a computed subquery, not stored.
- **Conditional fields** are nullable columns on `documents`; the form chooses which
  ones to render per `document_view`. **Locked extras:**
  - All views: `sender`, `document_form`, `language`, `related_document_number`,
    `related_document_date`, `archive_folder_id`
  - `incoming`: + `received_date`, `origin_organization`
  - `outgoing`: + `sent_date`, `recipient_organization`
  - `internal`: + (no extras)
  - `appeal`: + `applicant_full_name`, `applicant_phone`
- **Migrations.** One Alembic revision per phase. After autogenerate, manually replace
  `src.infrastructure...GUID(length=36)` with `sa.String(length=36)` per CLAUDE.md.

## Dependency Graph

```
Department model + migration
    │
    ├── Department API (CRUD)
    │       │
    │       └── Department admin UI (card grid)
    │
    └── (User wiring deferred to future phase)

Archive Folder model + migration  (independent of Department)
    │
    ├── Archive Folder API
    │       │
    │       └── Archive Folder list UI
    │
    └── Document.archive_folder_id (added in Phase 3 migration)

Document new columns + migration
    │
    ├── Document API (extended)
    │       │
    │       └── Document create/edit form (conditional fields)
    │
    └── Document detail page (display new fields)
```

## Phase 1: Department (Bo'lim)

### Task 1.1: Department domain + migration

**Description:** New aggregate `Department`. Fields: `id (GUID), name (String 255,
unique), description (Text, nullable), is_active (Boolean, default true), created_at,
updated_at`.

**Acceptance criteria:**
- [ ] `domain/department/entity.py` defines `Department` with `activate()` /
      `deactivate()` methods
- [ ] `DepartmentModel` in `infrastructure/persistence/models.py`
- [ ] Repository interface + SQLAlchemy implementation
- [ ] Alembic migration creates `departments` table; runs cleanly on a fresh SQLite DB
- [ ] No code outside the new aggregate is modified

**Verification:**
- [ ] `make migrate` succeeds on a fresh DB
- [ ] `python -c "from src.infrastructure.persistence.models import DepartmentModel; print(DepartmentModel.__tablename__)"`

**Dependencies:** None
**Files likely touched:** ~6
**Estimated scope:** M

---

### Task 1.2: Department API

**Description:** Application handlers, schemas, FastAPI routes.

**Acceptance criteria:**
- [ ] `application/department/{commands,queries,handlers}.py` with Create / Update /
      Delete / Activate / Deactivate commands and List / Get queries
- [ ] `api/schemas/department.py`
- [ ] `api/routes/department_routes.py` registered as `/api/departments`
- [ ] Endpoints: `GET|POST /api/departments`, `GET|PUT|DELETE /api/departments/:id`,
      `POST /api/departments/:id/activate`, `POST /api/departments/:id/deactivate`
- [ ] Mutating routes require `require_admin`; reads require `get_current_user`
- [ ] Optional `?active_only=true` filter on list

**Verification:**
- [ ] `curl -X POST /api/departments` with admin JWT returns 201
- [ ] `curl GET /api/departments` returns the list

**Dependencies:** 1.1
**Files likely touched:** ~5
**Estimated scope:** M

---

### Task 1.3: Frontend types + composable + label map

**Description:** Add `DepartmentResponse` to `app/types/index.ts`. Create
`app/composables/useDepartments.ts` mirroring `usePersons.ts`. Create
`app/utils/labels.ts` with the Uzbek label map. Sidebar nav adds "Bo'limlar".

**Acceptance criteria:**
- [ ] `DepartmentResponse` defined
- [ ] `useDepartments()` exposes `list()`, `get(id)`, `create()`, `update(id)`,
      `remove(id)`, `activate(id)`, `deactivate(id)`
- [ ] `labels.ts` exports `LABELS.department = "Bo'lim"`, etc.
- [ ] Sidebar shows "Bo'limlar" entry for admins (uses `LABELS.department + "lar"`
      OR a static string — pick one and document)

**Verification:**
- [ ] `npm run build` succeeds with no TS errors
- [ ] Sidebar renders "Bo'limlar" after admin login

**Dependencies:** 1.2
**Files likely touched:** 4
**Estimated scope:** S

---

### Task 1.4: Departments admin page (card grid)

**Description:** `/admin/departments/index.vue` — card grid like the reference screenshot.
Each card shows department name; edit pencil icon opens modal; "Bo'lim qo'shish" button
opens create modal.

**Acceptance criteria:**
- [ ] Page lists all departments as cards (3–4 per row, responsive)
- [ ] Create modal: name (required), description (optional)
- [ ] Edit modal pre-fills + supports rename / description edit
- [ ] Delete confirmation (`UModal`); if backend returns 409 (in-use), surface a toast
- [ ] Breadcrumb: Arxivist › Bo'limlar
- [ ] All visible labels Uzbek (sourced from `labels.ts`); primary color `madaniyat`

**Verification:**
- [ ] Manual: create, rename, delete a department end-to-end
- [ ] Visual: matches reference screenshot proportions

**Dependencies:** 1.3
**Files likely touched:** 1
**Estimated scope:** M

---

### Checkpoint: After Phase 1

- [ ] `make migrate` clean on fresh + populated DBs
- [ ] `make backend` + `make frontend` start without errors
- [ ] Admin can create / rename / activate-deactivate / delete a department
- [ ] No regression: archive flow (year → category → document) still works
- [ ] Commit Phase 1
- [ ] **Human review before Phase 2**

---

## Phase 2: Archive Folder (Yig'ma jild)

### Task 2.1: Archive Folder domain + migration

**Description:** Aggregate `ArchiveFolder` with fields: `id (GUID), index_code
(String 100), title (String 500), retention_period (String 20, enum value), start_date
(Date), end_date (Date, nullable), year_id (FK → years.id, nullable), created_at,
updated_at`. Unique constraint on `(year_id, index_code)`.

`RetentionPeriod` enum: `3_years | 5_years | 10_years | 25_years | 50_years | 75_years
| permanent | epk` (rendered via `labels.ts`).

**Acceptance criteria:**
- [ ] `domain/archive_folder/entity.py`
- [ ] `ArchiveFolderModel` with unique constraint on `(year_id, index_code)`
- [ ] Repository interface + impl
- [ ] Alembic migration

**Verification:**
- [ ] `make migrate` clean
- [ ] Unique constraint rejects duplicate `(year_id, index_code)`

**Dependencies:** None (independent of Phase 1)
**Files likely touched:** ~6
**Estimated scope:** M

---

### Task 2.2: Archive Folder API

**Description:** CRUD + list with optional `?year_id=` and `?search=` filters. List
response includes `document_count` (hardcoded 0 with TODO until Phase 3 wires the FK).

**Acceptance criteria:**
- [ ] `GET|POST /api/archive-folders`
- [ ] `GET|PUT|DELETE /api/archive-folders/:id`
- [ ] List filter: `?year_id=<id>&search=<title>`
- [ ] Response includes `document_count` (= 0 until Phase 3)

**Verification:**
- [ ] `curl POST /api/archive-folders` creates and returns 201
- [ ] List filter narrows correctly by year

**Dependencies:** 2.1
**Files likely touched:** ~5
**Estimated scope:** M

---

### Task 2.3: Frontend types + composable + sidebar entry

**Description:** `ArchiveFolderResponse` type, `useArchiveFolders()` composable,
extend `labels.ts` with the 7 column labels. Sidebar adds "Yig'ma jildlar".

**Acceptance criteria:**
- [ ] Type matches API response
- [ ] Composable exposes CRUD
- [ ] `labels.ts` adds `archive_folder`, `index_code`, `title`, `retention_period`,
      `start_date`, `end_date`, `document_count`
- [ ] Sidebar visible to admins (others deferred)

**Verification:**
- [ ] `npm run build` succeeds

**Dependencies:** 2.2
**Files likely touched:** 4
**Estimated scope:** S

---

### Task 2.4: Archive Folder list page

**Description:** `/archive-folders/index.vue`. UTable with 7 columns: row number,
`index_code → "Yig'ma jild indeksi"`, `title → "Sarlavha"`,
`retention_period → "Saqlash muddati"`, `start_date → "Boshlanish sanasi"`,
`end_date → "Tugash sanasi"`, `document_count → "Hujjatlar soni"`. Year filter
dropdown (uses `/api/years`). Create/edit modal with DatePicker.

**Acceptance criteria:**
- [ ] Table columns labeled exactly as above (from `labels.ts`)
- [ ] Year filter dropdown
- [ ] Create modal with all fields
- [ ] Empty state when no folders
- [ ] T/r column = index in list + 1

**Verification:**
- [ ] Manual: create archive folder, see it listed, edit, delete

**Dependencies:** 2.3
**Files likely touched:** 1–2
**Estimated scope:** M

---

### Checkpoint: After Phase 2

- [ ] Archive folders CRUD end-to-end works
- [ ] `document_count` shows 0 for all (Phase 3 wires it)
- [ ] No regression on archive or Phase 1
- [ ] Commit Phase 2

---

## Phase 3: Document overhaul

### Task 3.1: Document model: new columns + Archive Folder FK

**Description:** Add columns to `documents`:
- `document_view (String 20, NOT NULL, default 'unknown' for backfill)`
- `archive_folder_id (GUID, nullable, FK → archive_folders.id ON DELETE SET NULL)`
- `document_form (String 100, nullable)`
- `sender (String 255, nullable)`
- `language (String 20, nullable)`
- `related_document_number (String 100, nullable)`
- `related_document_date (Date, nullable)`
- View-specific extras (see Open Questions for confirmation):
  - `received_date (Date, nullable)`, `origin_organization (String 255, nullable)`
  - `sent_date (Date, nullable)`, `recipient_organization (String 255, nullable)`
  - `applicant_full_name (String 255, nullable)`, `applicant_phone (String 50, nullable)`

**Acceptance criteria:**
- [ ] Enum `DocumentView` with `INCOMING / OUTGOING / INTERNAL / APPEAL / UNKNOWN`
- [ ] All new columns on `DocumentModel` + `Document` entity
- [ ] Migration runs cleanly on populated DB; legacy rows get
      `document_view='unknown'`
- [ ] FK to `archive_folders.id` with `ON DELETE SET NULL`

**Verification:**
- [ ] `make migrate` against the populated DB — row count unchanged, every row has
      `document_view != NULL`

**Dependencies:** 2.1
**Files likely touched:** ~3
**Estimated scope:** M

---

### Task 3.2: Document API extended

**Description:** Update `CreateDocumentRequest`, `UpdateDocumentRequest`,
`DocumentResponse`. Server-side validation: required extras must be present per
`document_view`. List endpoint accepts `?document_view=` and `?archive_folder_id=`.

**Acceptance criteria:**
- [ ] Pydantic models accept all new fields
- [ ] 422 when `document_view=incoming` but required extras missing
- [ ] List filters work; pagination unchanged
- [ ] `archive_folder_id` on document updates the next
      `archive-folders` list response's `document_count`

**Verification:**
- [ ] `curl POST /api/documents` with `document_view=incoming` succeeds;
      missing required extra returns 422 with clear error

**Dependencies:** 3.1, 2.2
**Files likely touched:** ~3
**Estimated scope:** M

---

### Task 3.3: Archive Folder list shows real document counts

**Description:** Replace the hardcoded `0` in the archive folders list query with a
real `COUNT(documents.id) GROUP BY archive_folder_id` subquery. Single round-trip.

**Acceptance criteria:**
- [ ] List response shows accurate `document_count`
- [ ] No N+1: confirm by `SQLALCHEMY_ECHO=true` and inspecting one round-trip per list

**Verification:**
- [ ] Create 3 documents in one archive folder → list shows `document_count=3`

**Dependencies:** 3.2
**Files likely touched:** 1
**Estimated scope:** XS

---

### Task 3.4: Document create form with conditional fields

**Description:** Update `/archive/:year/:categoryId/create.vue`. Add `Hujjat
ko'rinishi` select (4 options from `labels.ts`). On change, render the correct field
set. Add common new fields. Add archive folder select cascaded on year. Match the
reference form layout (second screenshot).

**Acceptance criteria:**
- [ ] All common fields present and posted to API using English keys
- [ ] All visible labels Uzbek (sourced from `labels.ts`)
- [ ] Conditional fields shown/hidden based on `document_view`
- [ ] Archive folder select filtered by the year of the document
- [ ] Form validation matches backend (required extras)
- [ ] Existing dynamic category fields (EAV) still rendered below the new fields

**Verification:**
- [ ] Manual: create one document of each `document_view`, confirm extras appear
      and persist
- [ ] Existing categories with custom fields still work

**Dependencies:** 3.3
**Files likely touched:** 2–3
**Estimated scope:** L → split if >5 files

---

### Task 3.5: Document edit + detail pages reflect new fields

**Description:** Update `/archive/:year/:categoryId/:id/edit.vue` and the detail page
to show/edit the new fields. Detail page shows an "Yig'ma jild" link if assigned.

**Acceptance criteria:**
- [ ] Edit form is symmetric with create form
- [ ] Detail page renders new fields in a clear sectioned layout
- [ ] Archive folder displayed as a link to its (stub or future) detail page

**Verification:**
- [ ] Manual: edit a document's view from Incoming → Outgoing; required-extra
      validation triggers; switch is persisted

**Dependencies:** 3.4
**Files likely touched:** 2
**Estimated scope:** M

---

### Checkpoint: After Phase 3

- [ ] All three reference-screenshot features visible and functional
- [ ] No regression on attachments, person assignment, PDF preview
- [ ] All migrations apply cleanly on a fresh AND populated DB
- [ ] Commit Phase 3
- [ ] **Human review before release tag**

---

## Parallelization Opportunities

- Phases run **sequentially** (each ends with a checkpoint).
- Within Phase 1: Tasks 1.1–1.4 are sequential.
- Within Phase 2: Tasks 2.1–2.4 are sequential.
- Phase 1 and Phase 2 backends are independent and could run in parallel by two
  agents if needed — they share only `models.py` (merge conflict risk: low, append-only).
- Phase 3 must be sequential (3.1 → 3.2/3.3 → 3.4 → 3.5).

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Conditional-field spec for `appeal` / `incoming` / `outgoing` extras is guessed | Med | Confirm with user before Task 3.1 (Open Questions). Only Tasks 3.1/3.2/3.4 schemas shift if list differs — bounded blast radius. |
| Archive folder `index_code` uniqueness scope (per year vs. global) | Low | Default per-year, matches archival convention. Cheap to relax later. |
| Department deletion when something later references it | Med | Backend returns 409; UI shows toast. When User↔Department link is added in a future phase, switch to `ON DELETE SET NULL`. |
| Forgotten `GUID(length=36)` → `sa.String(length=36)` swap in autogen migration breaks SQLite | High | Add to checkpoint checklist; review each migration diff before commit. |
| Uzbek labels drift between sidebar, table headers, form labels | Low | Single source `app/utils/labels.ts`; templates import the map and never inline Uzbek strings except in `labels.ts`. |

## Open Questions

All blocking questions resolved. Non-blocking items:

1. **"Ko'rsatmalar" top-right link** — out of scope; ignore for now.

### Resolved

- ~~Retention period format~~ → **enum** locked: `3_years, 5_years, 10_years, 25_years,
  50_years, 75_years, permanent, epk` (Uzbek labels in `labels.ts`).
- ~~Conditional extras per `document_view`~~ → **locked** as proposed:
  - `incoming`: `received_date`, `origin_organization`
  - `outgoing`: `sent_date`, `recipient_organization`
  - `internal`: (no extras beyond the common set)
  - `appeal`: `applicant_full_name`, `applicant_phone`

## Verification (pre-implementation)

- [x] Every task has acceptance criteria
- [x] Every task has a verification step
- [x] Task dependencies identified and ordered
- [x] No task touches more than ~5 files (3.4 flagged for split if needed)
- [x] Checkpoints between phases
- [ ] Human has reviewed and approved this plan

---

# Plan v2: Full-text indexing (OCR + Elasticsearch + Postgres + Advanced Search)

## Overview

The archive currently stores documents in SQLite with file uploads on local disk. Search
is metadata-only (title, document_number, short_desc, signer, archive_number via
`ILIKE`). This plan adds:

1. **Postgres as the production database** — currently configured in `config.py` but
   never actually used. Promote it to dev+prod, with a path to migrate existing SQLite
   data.
2. **OCR pipeline** — extract text from every uploaded PDF / image (main file +
   attachments) using Tesseract. Store extracted text in Postgres so we can reindex
   without re-OCR.
3. **Elasticsearch index** — denormalized per-document index with all metadata
   (year/category/person/archive folder/document type) plus OCR text. ES becomes the
   read path for search.
4. **Advanced search page** — new `/archive/search` route with full-text query,
   highlighted snippets, faceted filters (year, category, document_view, document_type,
   archive folder, person, date range), and pagination.

## Locked Defaults (avoid 20 round-trip questions)

These choices are locked. Call out before Phase 4.1 starts if you want to change them.

| Concern | Choice | Why |
|---------|--------|-----|
| OCR engine | **Tesseract 5** via `pytesseract` + `pdf2image` (Poppler) | Free, ships with Uzbek (`uzb`, `uzb_cyrl`), Russian (`rus`), English (`eng`) language packs. Mature. |
| PDF text path | **PyMuPDF (`fitz`) first; Tesseract fallback** when extracted text length < 100 chars | Fast path: ~90% of digital PDFs already have embedded text. OCR only for scanned. |
| Image OCR | **Tesseract directly on JPG/PNG/TIFF** | One engine for everything. |
| Queue | **`arq` + Redis** | Async-native, matches FastAPI's async style, ~200 LOC dependency, no Celery boilerplate. |
| Search engine | **Elasticsearch 8.x** (single node, security disabled in dev) | Industry standard. Best Uzbek/Russian language support via ICU + Russian stemmer. |
| ES client | **`elasticsearch[async]` 8.x** | Official, async support. |
| Index strategy | **Single index `documents-v1` + alias `documents`** | Versioned alias enables zero-downtime reindex. |
| Analyzer | **Custom multi-lingual: ICU tokenizer + Russian stemmer + lowercase + edge-ngram (2–10) for autocomplete** | Uzbek mixes Cyrillic + Latin; Russian content common. ICU handles both. |
| Postgres types | **Real `UUID` + `JSONB` (`postgresql.UUID(as_uuid=True)`, `postgresql.JSONB`)** when DB is Postgres; keep the existing `GUID`/`JSON` shims as fallback for SQLite | CLAUDE.md notes the current shim — promote to real types where the DB supports them. |
| Data move | **One-shot Python script reading from SQLite, writing to Postgres** | Existing data is small; one batch job is enough. No Alembic gymnastics needed — the schema already exists in Postgres after running migrations. |
| Dev infra | **Docker Compose** at repo root: `postgres`, `redis`, `elasticsearch`, `kibana` (optional, profile) | One `docker compose up -d` to get the whole stack. |
| Sync trigger | **Outbox-lite**: write changes to a `search_index_jobs` table inside the same DB transaction as the document save, then arq worker drains it | Avoids the "saved but not indexed" failure mode of fire-and-forget background tasks. Cheap to build, robust under crash. |
| Highlight tags | **`<mark>` HTML tags** rendered via `v-html` (sanitised in template) | Standard ES convention; safe because ES only emits the tag, not user-controllable. |

If any of these is wrong for the deployment target, push back **before Phase 4.1**.
Switching engines mid-plan invalidates ~half the tasks.

## Architecture

```
┌──────────────┐   ┌──────────────────────────────────────────────┐
│   Frontend   │──▶│              FastAPI /api/search             │
│  /archive/   │   │   - Builds ES query from filters + facets    │
│   search     │◀──│   - Returns hits + highlights + facet counts │
└──────────────┘   └──────────────────────────────────────────────┘
                            │                          ▲
                            ▼                          │
                   ┌────────────────┐         ┌────────┴────────┐
                   │  Elasticsearch │         │   Postgres      │
                   │   documents    │◀────────│   (source of    │
                   │   (denorm)     │  index  │    truth)       │
                   └────────────────┘         └────────┬────────┘
                            ▲                          │
                            │ bulk index               │ outbox row
                            │                          ▼
                   ┌────────┴────────┐         ┌───────────────────┐
                   │   arq worker    │◀────────│ search_index_jobs │
                   │   (async)       │         │ (outbox table)    │
                   └────────┬────────┘         └───────────────────┘
                            │
                ┌───────────┴────────────┐
                ▼                        ▼
        ┌──────────────┐         ┌──────────────────┐
        │ OCR pipeline │         │  File storage    │
        │ PyMuPDF→Tess │◀────────│  uploads/*.pdf   │
        │ writes back  │         │  /attachments/   │
        │ to Postgres  │         └──────────────────┘
        │ document_text│
        │ attachment_  │
        │ text columns │
        └──────────────┘
```

## Dependency Graph

```
Phase 4: Infrastructure & Postgres production-ready
    │
    ├── 4.1 Docker Compose (postgres + redis + elasticsearch)
    │       │
    │       ├── 4.2 Postgres type promotion (UUID, JSONB)
    │       │       │
    │       │       └── 4.3 Migration run + data move script
    │       │
    │       └── 4.4 arq worker bootstrap (no jobs yet — just the runtime)
    │
Phase 5: Elasticsearch indexing of metadata (no OCR yet)
    │
    ├── 5.1 ES client + index template + alias
    │       │
    │       ├── 5.2 Indexer service (Postgres → ES bulk)
    │       │       │
    │       │       ├── 5.3 search_index_jobs outbox + repo + on-save hook
    │       │       │       │
    │       │       │       └── 5.4 arq job: drain outbox → index/delete in ES
    │       │       │
    │       │       └── 5.5 Reindex CLI (full reindex from scratch)
    │       │
    │       └── 5.6 Health endpoint includes ES + Redis status
    │
Phase 6: OCR pipeline
    │
    ├── 6.1 OCR service abstraction (Tesseract + PyMuPDF)
    │       │
    │       ├── 6.2 document_text + attachment_text columns + migration
    │       │       │
    │       │       ├── 6.3 arq job: extract on upload → write to DB → enqueue reindex
    │       │       │
    │       │       └── 6.4 Backfill CLI: OCR all existing documents
    │       │
    │       └── 6.5 OCR status visible in document detail (badge: pending/done/failed)
    │
Phase 7: Advanced search UI + API
    │
    ├── 7.1 Search API (POST /api/search) with filters + facets + highlights
    │       │
    │       ├── 7.2 Frontend search page route + types + composable
    │       │       │
    │       │       └── 7.3 Filters panel + result cards + highlight rendering
    │       │
    │       └── 7.4 Global search box in dashboard header → /archive/search?q=…
```

---

## Phase 4: Infrastructure & Postgres production-ready

### Task 4.1: Docker Compose for dev stack

**Description:** Single `docker-compose.yml` at repo root running Postgres 16,
Redis 7, Elasticsearch 8.x (single-node, security off), Kibana (optional profile
`tools`). Add `.env.example`. Update README with `docker compose up -d` flow.

**Acceptance criteria:**
- [ ] `docker-compose.yml` with services: `postgres`, `redis`, `elasticsearch`,
      `kibana` (profile `tools`)
- [ ] Postgres exposes 5432; Redis 6379; ES 9200; Kibana 5601
- [ ] Named volumes for postgres data + ES data
- [ ] ES env: `discovery.type=single-node`, `xpack.security.enabled=false`,
      `ES_JAVA_OPTS=-Xms1g -Xmx1g`
- [ ] `.env.example` documents `DATABASE_URL`, `REDIS_URL`, `ELASTICSEARCH_URL`
- [ ] README section: "Local dev stack"

**Verification:**
- [ ] `docker compose up -d` — all three containers healthy
- [ ] `curl http://localhost:9200` returns ES cluster info
- [ ] `redis-cli ping` returns PONG
- [ ] `psql postgresql://postgres:postgres@localhost:5432/arxiv_db -c '\\l'` lists `arxiv_db`

**Dependencies:** None
**Files likely touched:** 3 (new docker-compose.yml, new .env.example, README edit)
**Estimated scope:** S

---

### Task 4.2: Postgres-aware types in models

**Description:** Replace `GUID(length=36)` with `postgresql.UUID(as_uuid=True)` and
`JSON` with `postgresql.JSONB` when running on Postgres. The custom shims stay as
fallback for SQLite (existing dev `.db.bak`). Use SQLAlchemy's
`.with_variant(...)` pattern so a single column type adapts per dialect.

**Acceptance criteria:**
- [ ] All `GUID` columns use `String(36).with_variant(pg.UUID(as_uuid=True), "postgresql")`
- [ ] All `JSON` columns use `sa.JSON.with_variant(pg.JSONB, "postgresql")`
- [ ] Existing SQLite migrations still run unchanged on `arxiv_db.db.bak`
- [ ] New migration generated on a Postgres target writes `UUID` / `JSONB` literally

**Verification:**
- [ ] `alembic upgrade head` on a fresh **SQLite** DB — unchanged behaviour
- [ ] `alembic upgrade head` on a fresh **Postgres** DB — succeeds, `\d documents`
      shows real `uuid` and `jsonb` types
- [ ] Existing tests / smoke flow (login → list documents) works against Postgres

**Dependencies:** 4.1
**Files likely touched:** ~2 (`models.py`, possibly one new alembic revision)
**Estimated scope:** M

---

### Task 4.3: SQLite → Postgres data migration script

**Description:** Standalone script `backend/scripts/migrate_sqlite_to_postgres.py`
that opens both DBs, reads every table in dependency order, and inserts into
Postgres. Idempotent (truncates target tables first, behind a `--yes-i-mean-it`
flag). Preserves UUIDs and dates exactly.

**Acceptance criteria:**
- [ ] Script reads tables in FK dependency order
- [ ] `--source-url` and `--target-url` flags (defaults to env vars)
- [ ] `--yes-i-mean-it` required to truncate target
- [ ] All 18 tables copied (users, years, categories, category_fields, default_fields,
      documents, document_field_values, document_attachments, persons, tenures,
      departments, archive_folders, document_types, regions, countries,
      reception_places, appeal_types, retention_periods)
- [ ] Row counts match source DB
- [ ] Logs warning if any FK violation skipped

**Verification:**
- [ ] Run script against `backend/arxiv_db.db.bak` → fresh Postgres
- [ ] Row count assertions: `SELECT count(*) FROM <each table>` matches source
- [ ] App boots and lists all documents from Postgres correctly
- [ ] `make backend` switches to Postgres via env var

**Dependencies:** 4.2
**Files likely touched:** 1 new
**Estimated scope:** M

---

### Task 4.4: arq worker bootstrap

**Description:** Add `arq` to deps. Create `backend/src/infrastructure/jobs/worker.py`
with an empty `WorkerSettings` and a placeholder job. Add `make worker` to start it.
This is just the runtime; Phase 5 and 6 add actual jobs.

**Acceptance criteria:**
- [ ] `arq` added to `pyproject.toml`
- [ ] `worker.py` defines `WorkerSettings` with Redis connection from settings
- [ ] One placeholder job `health_check()` that logs and returns OK
- [ ] `make worker` (or documented one-liner) starts the worker
- [ ] Worker connects to Redis and idles waiting for jobs

**Verification:**
- [ ] Start worker → log shows "Connected to redis" and no errors
- [ ] From a Python shell: enqueue `health_check` → worker logs "ok"

**Dependencies:** 4.1
**Files likely touched:** 2 (worker.py + pyproject + Makefile)
**Estimated scope:** S

---

### Checkpoint: After Phase 4

- [ ] `docker compose up -d` brings up the full stack
- [ ] `alembic upgrade head` runs cleanly against Postgres
- [ ] Existing dev DB migrated; app works identically on Postgres
- [ ] arq worker connects and runs the placeholder job
- [ ] **No user-visible feature change yet** (this phase is foundational)
- [ ] Commit Phase 4
- [ ] **Human review before Phase 5**

---

## Phase 5: Elasticsearch indexing of metadata (full-text on existing data, no OCR yet)

This phase delivers user-visible value: existing search becomes a real full-text
engine over all metadata + dynamic fields, with much better matching than ILIKE.

### Task 5.1: ES client + index template + alias

**Description:** `backend/src/infrastructure/search/es_client.py` builds an async
`AsyncElasticsearch` from `settings.elasticsearch_url`. `index_template.py` defines
mapping for the `documents-v1` index. Create alias `documents → documents-v1`.

**Mapping (key fields):**
- `id` (keyword), `year_id` (long), `year_value` (long), `category_id` (keyword),
  `category_name` (text + keyword), `title` (text), `document_number` (keyword + text),
  `short_desc` (text), `signer` (text), `archive_number` (keyword),
  `person_name` (text), `person_position` (text), `archive_folder_id` (keyword),
  `archive_folder_title` (text), `document_type_id` (keyword),
  `document_type_name` (text + keyword), `document_view` (keyword),
  `date` (date), `created_at` (date), `extracted_text` (text — empty in Phase 5),
  `attachments` (nested: filename, extracted_text), `field_values` (nested: name, value),
  plus all view-specific fields (sender, language, document_form, etc.) as keyword/text

**Analyzer:**
- `uz_multi` analyzer: `icu_tokenizer` + `lowercase` + `icu_folding` + `russian_stemmer`
- `uz_autocomplete` analyzer: same + `edge_ngram(2, 10)` for prefix matching on titles

**Acceptance criteria:**
- [ ] `es_client.py` exports `get_es() -> AsyncElasticsearch` (lazy singleton)
- [ ] `index_template.py` declares the full mapping
- [ ] `ensure_index()` function creates `documents-v1` if missing and points alias `documents` at it
- [ ] `elasticsearch[async]>=8.0` in pyproject
- [ ] Plugin `analysis-icu` enabled in docker-compose ES image (build step or volume)

**Verification:**
- [ ] App startup calls `ensure_index()`; `curl http://localhost:9200/_alias/documents`
      shows the alias
- [ ] `curl http://localhost:9200/documents/_mapping` shows the mapping

**Dependencies:** 4.1, 4.2
**Files likely touched:** 3 new
**Estimated scope:** M

---

### Task 5.2: Indexer service (Postgres → ES)

**Description:** `backend/src/infrastructure/search/document_indexer.py` exposes
`index_document(doc_id)` and `delete_document(doc_id)`. Reads denormalized fields
from Postgres (joins year/category/person/archive_folder/document_type +
field_values + attachments), builds the ES doc, and writes/deletes via the client.
Uses `op_type=index` (upsert) for write.

**Acceptance criteria:**
- [ ] `index_document(uuid)` — reads doc + joins, writes to `documents` alias
- [ ] `delete_document(uuid)` — deletes by ID; tolerates 404
- [ ] `index_bulk(list[uuid])` — single bulk request for backfill
- [ ] Mapper handles missing FKs (deleted category/person/etc.) — uses `None`,
      never raises

**Verification:**
- [ ] Manually index one document → `curl /documents/_search?q=<title>` returns it
- [ ] Delete it → query returns no hits

**Dependencies:** 5.1
**Files likely touched:** 2 new
**Estimated scope:** M

---

### Task 5.3: search_index_jobs outbox + on-save hook

**Description:** New table `search_index_jobs` with `id, document_id, op (index|delete),
created_at`. Document repository writes a row in the same transaction as `save()` and
`delete()`. This guarantees: if the DB transaction commits, the index job exists.

**Acceptance criteria:**
- [ ] Migration creates `search_index_jobs` with PK + `(document_id, created_at)` index
- [ ] `SqlAlchemyDocumentRepository.save()` and `.delete()` insert an outbox row
- [ ] Insert happens before `session.commit()`; no separate transaction
- [ ] Compatible with existing edit/delete flows — no API contract change

**Verification:**
- [ ] Create a document via API → `SELECT * FROM search_index_jobs` shows one row with op=`index`
- [ ] Delete a document → outbox has op=`delete`

**Dependencies:** 4.2
**Files likely touched:** 3 (`models.py`, document_repository.py, new alembic revision)
**Estimated scope:** M

---

### Task 5.4: arq worker drains the outbox

**Description:** arq cron job `drain_search_outbox()` runs every 2 seconds (configurable).
Reads up to 100 jobs in `created_at` order, calls `document_indexer.index_document()`
or `.delete_document()`, deletes the row on success, leaves it on failure (next run
retries). Add structured logging.

**Acceptance criteria:**
- [ ] Cron job registered in `WorkerSettings.cron_jobs`, runs every 2s
- [ ] Batch size 100; processes oldest first
- [ ] On ES failure: log error, keep row (retry next tick)
- [ ] On Postgres 404 (doc deleted between enqueue and process for `index` op):
      convert to delete-in-ES; log info
- [ ] After processing a row: delete from outbox in same transaction

**Verification:**
- [ ] Create 10 docs in a loop → outbox drains to empty within 5s
- [ ] Stop ES; create docs → outbox grows; restart ES → outbox drains
- [ ] Search returns the indexed docs

**Dependencies:** 5.2, 5.3, 4.4
**Files likely touched:** 1 (worker.py update)
**Estimated scope:** M

---

### Task 5.5: Reindex CLI

**Description:** `python -m src.scripts.reindex` walks all documents and inserts an
outbox row for each. Optional flags: `--year <value>`, `--since <iso-date>`, `--dry-run`.
Useful after mapping changes or fresh-stack bringup.

**Acceptance criteria:**
- [ ] CLI prints count before starting + after
- [ ] Inserts outbox rows in batches of 500
- [ ] `--dry-run` skips inserts but prints count
- [ ] Documented in README

**Verification:**
- [ ] Truncate ES; run reindex; wait for outbox drain; verify ES doc count = DB doc count

**Dependencies:** 5.4
**Files likely touched:** 1 new
**Estimated scope:** S

---

### Task 5.6: Health endpoint reports ES + Redis status

**Description:** Extend `GET /api/health` to ping ES and Redis. Returns
`{"status": "ok", "postgres": "ok", "elasticsearch": "ok", "redis": "ok"}`. Returns
503 if any check fails.

**Acceptance criteria:**
- [ ] Pings DB (existing), ES (`cluster.health` with 1s timeout), Redis (ping)
- [ ] Returns 200 only if all three are healthy
- [ ] Logs which dependency is down

**Verification:**
- [ ] Stop ES → `/api/health` returns 503 + `"elasticsearch": "down"`

**Dependencies:** 5.1, 4.4
**Files likely touched:** 1
**Estimated scope:** XS

---

### Checkpoint: After Phase 5

- [ ] Every existing document is searchable in ES via `documents` alias
- [ ] Create/edit/delete a document → ES reflects within 5 seconds
- [ ] Reindex CLI works end-to-end
- [ ] Health endpoint reports all three dependencies
- [ ] **Existing search UI still uses the old ILIKE path** (cut-over happens in Phase 7)
- [ ] Commit Phase 5
- [ ] **Human review before Phase 6**

---

## Phase 6: OCR pipeline

### Task 6.1: OCR service abstraction

**Description:** `backend/src/infrastructure/ocr/ocr_service.py` exposes
`extract_text(file_path: Path, mime: str) -> str`. Algorithm:

1. If PDF: try `fitz.open(path).extract_text()` per page; concat. If total length <
   100 chars → fall through to Tesseract via `pdf2image` → `pytesseract.image_to_string`
2. If image (`.png/.jpg/.tif/.tiff`): `pytesseract.image_to_string(Image.open(path))`
3. Else: empty string + log warning

All Tesseract calls use `lang="uzb+rus+eng"` (Cyrillic Uzbek packs are
`uzb_cyrl`; auto-detect by trying both and keeping the longer result).

**Acceptance criteria:**
- [ ] `pytesseract`, `pdf2image`, `Pillow`, `PyMuPDF` in pyproject
- [ ] Tesseract binary + Poppler documented as system deps (Windows: chocolatey; Linux: apt)
- [ ] `extract_text()` handles PDF, PNG, JPG, TIFF
- [ ] Falls back to OCR only when embedded text is sparse
- [ ] Function is sync (CPU-bound) but wrapped in `run_in_executor` for async callers

**Verification:**
- [ ] Test on a known scanned PDF → returns non-empty Uzbek text
- [ ] Test on a digital PDF (text layer present) → returns text without invoking Tesseract
      (verify via log marker)

**Dependencies:** 4.1 (Docker image must include `tesseract-ocr` + `poppler-utils` if
the worker runs in Docker)
**Files likely touched:** 2 new (ocr_service + Dockerfile.worker)
**Estimated scope:** L → split if Tesseract Windows setup is painful

---

### Task 6.2: document_text + attachment_text columns + migration

**Description:** Add columns:
- `documents.extracted_text TEXT NULL`
- `documents.ocr_status VARCHAR(20) DEFAULT 'pending'` (values: `pending|processing|done|failed|skipped`)
- `documents.ocr_completed_at TIMESTAMP NULL`
- `document_attachments.extracted_text TEXT NULL`
- `document_attachments.ocr_status VARCHAR(20) DEFAULT 'pending'`
- `document_attachments.ocr_completed_at TIMESTAMP NULL`

**Acceptance criteria:**
- [ ] Alembic migration adds the six columns
- [ ] Existing rows get `ocr_status='pending'` (Phase 6.4 backfill picks them up)
- [ ] Runs cleanly on Postgres and SQLite
- [ ] Models + mappers + Pydantic responses include the new fields

**Verification:**
- [ ] `alembic upgrade head` on the dev DB; `\d documents` shows the columns
- [ ] API list returns `ocr_status` field

**Dependencies:** 4.2
**Files likely touched:** 4 (models, mappers, schemas, new migration)
**Estimated scope:** M

---

### Task 6.3: arq job — OCR on upload

**Description:** When a file is uploaded (`POST /api/documents/:id/file` or
`/attachments`), enqueue `ocr_extract(document_id, attachment_id?)`. Job: set status
`processing` → call `ocr_service.extract_text` → write text + status `done` to DB →
insert a `search_index_jobs` row so the doc gets re-indexed with the new text.

**Acceptance criteria:**
- [ ] Both upload endpoints enqueue the job after the file write commits
- [ ] Job updates `ocr_status` to `processing` immediately so UI can show progress
- [ ] On success: writes `extracted_text` + `ocr_status=done` + `ocr_completed_at`
- [ ] On failure (Tesseract crash, file gone): `ocr_status=failed`; logged with full
      traceback; **does not block the request**
- [ ] After success → inserts outbox row → Phase 5.4 worker reindexes

**Verification:**
- [ ] Upload a scanned PDF → within 60s `ocr_status=done` and `extracted_text` is non-empty
- [ ] Search the page's content → document found
- [ ] Upload a corrupt file → `ocr_status=failed`, no crash

**Dependencies:** 6.1, 6.2, 5.4
**Files likely touched:** 3 (worker.py, document_routes.py, attachment route)
**Estimated scope:** M

---

### Task 6.4: Backfill CLI for existing documents

**Description:** `python -m src.scripts.ocr_backfill` finds all docs+attachments with
`ocr_status IN ('pending', 'failed')` and enqueues `ocr_extract` for each. Throttle:
N at a time (default 4). Resume-safe — re-running picks up where it left off.

**Acceptance criteria:**
- [ ] CLI lists how many docs/attachments will be processed
- [ ] `--concurrency N` flag (default 4)
- [ ] `--retry-failed` flag (default false; default is only `pending`)
- [ ] Prints progress every 10 jobs

**Verification:**
- [ ] Run on the dev DB → all docs eventually transition to `done` or `failed`
- [ ] Re-run → finds 0 new candidates

**Dependencies:** 6.3
**Files likely touched:** 1 new
**Estimated scope:** S

---

### Task 6.5: OCR status visible in UI

**Description:** Document detail page shows a small badge next to the file icon:
`OCR: tayyor` (green) / `OCR: jarayonda` (amber, animated) / `OCR: muvaffaqiyatsiz`
(red) / `OCR: kutmoqda` (neutral). Attachments list shows per-attachment status.

**Acceptance criteria:**
- [ ] Badge uses existing `UBadge` component, sourced from `labels.ts`
- [ ] Uzbek labels added: `ocr_pending → "Kutmoqda"`, `ocr_processing → "Jarayonda"`,
      `ocr_done → "Tayyor"`, `ocr_failed → "Muvaffaqiyatsiz"`, `ocr_skipped → "O'tkazib yuborildi"`
- [ ] Auto-refresh: page polls every 5s while any item is `processing`
- [ ] No layout shift — badge has fixed width

**Verification:**
- [ ] Upload a fresh PDF, observe the badge transitions pending → processing → done

**Dependencies:** 6.3
**Files likely touched:** 2 (detail page, labels.ts)
**Estimated scope:** S

---

### Checkpoint: After Phase 6

- [ ] All existing documents have `ocr_status=done` (or `failed` with logged reason)
- [ ] New uploads auto-OCR within ~60s for a typical 5-page PDF
- [ ] OCR text appears in ES search results (search a phrase from the body of a doc → found)
- [ ] Detail page badges reflect status
- [ ] Commit Phase 6
- [ ] **Human review before Phase 7**

---

## Phase 7: Advanced search UI + API

### Task 7.1: Search API endpoint

**Description:** `POST /api/search` accepts:

```json
{
  "q": "free text",
  "filters": {
    "year_id": [2023, 2024],
    "category_id": ["uuid", ...],
    "document_view": ["incoming"],
    "document_type_id": ["uuid"],
    "archive_folder_id": ["uuid"],
    "person_id": ["uuid"],
    "date_from": "2023-01-01",
    "date_to": "2024-12-31"
  },
  "facets": ["year_id", "category_id", "document_view", "document_type_id"],
  "page": 1,
  "page_size": 20,
  "sort": "relevance | date_desc | date_asc"
}
```

Returns `{ items, total, facets: { <field>: [{ value, count }] }, took_ms }`. Each
item includes `highlights` (snippet HTML around matches in title / short_desc /
extracted_text / attachments.extracted_text).

**Acceptance criteria:**
- [ ] Pydantic request + response schemas
- [ ] Builds ES query: `multi_match` on title^3, document_number^3, short_desc^2,
      signer, person_name, extracted_text, attachments.extracted_text
- [ ] Filters translate to ES `term` / `terms` / `range` clauses inside `bool.filter`
- [ ] Facet aggregations for `facets` list
- [ ] Highlight fields: title, short_desc, extracted_text (fragment_size=150,
      number_of_fragments=3), attachments.extracted_text
- [ ] Tokens: only `get_current_user` (any logged-in user can search)
- [ ] Empty `q` is valid (returns filtered list sorted by date_desc by default)

**Verification:**
- [ ] `curl POST /api/search` with `q="madaniyat"` returns hits + highlights
- [ ] Facet counts match a hand-counted SQL query

**Dependencies:** 5.4
**Files likely touched:** 3 new (route, schema, query builder)
**Estimated scope:** L

---

### Task 7.2: Frontend types + composable

**Description:** Add `SearchRequest`, `SearchResponse`, `SearchHit`, `Facet` types.
Create `useSearch()` composable with `search(params)` and a debounced reactive
`useSearchQuery(query: Ref, filters: Ref)` that auto-refetches.

**Acceptance criteria:**
- [ ] Types align with API schema exactly
- [ ] Composable debounces 300ms
- [ ] Cancels in-flight request when params change (AbortController)

**Verification:**
- [ ] `npm run build` succeeds with no TS errors

**Dependencies:** 7.1
**Files likely touched:** 2 (types, composable)
**Estimated scope:** S

---

### Task 7.3: Advanced search page

**Description:** `frontend/app/pages/archive/search.vue`. Layout:

```
┌─────────────────────────────────────────────────────────────┐
│  [Search bar — autofocus]   [Filtrlar (3) ▼]   [Tartiblash ▼]│
├──────────────┬──────────────────────────────────────────────┤
│ Filters      │ 142 ta natija topildi (12ms)                 │
│ ─ Yil        │ ┌──────────────────────────────────────────┐ │
│   ☐ 2024 (42)│ │ [PDF icon] [Hujjat nomi — link]          │ │
│   ☐ 2023 (38)│ │  ...short_desc with <mark> highlights... │ │
│ ─ Nomenkl    │ │  ...page 3 of attachment: "...<mark>...  │ │
│   ☐ ...      │ │  [Yil 2023] [Murojaat] [Hujjat turi]     │ │
│ ─ Hujjat     │ └──────────────────────────────────────────┘ │
│   ko'rinishi │ [more cards…]                                │
│   ☐ Kiruvchi │ [Pagination]                                 │
│   ☐ Chiquvchi│                                              │
│ ─ Sana       │                                              │
│   [Boshlang] │                                              │
│   [Tugash]   │                                              │
└──────────────┴──────────────────────────────────────────────┘
```

**Acceptance criteria:**
- [ ] Route: `/archive/search?q=…&year_id=…&…` (filters round-trip via URL)
- [ ] Filters panel: year (multi), category (multi), document_view (chips),
      document_type (multi), archive_folder (multi), date range
- [ ] Facet counts shown next to each filter option
- [ ] Result card: title link → existing document detail page, highlighted snippets
      (rendered with `v-html` — safe because ES emits only `<mark>` tags)
- [ ] Sort dropdown: relevance / date_desc / date_asc
- [ ] Pagination using `UPagination`
- [ ] Empty state: `EmptyState` component with helpful message
- [ ] Skeleton loading state — never blank flash
- [ ] All labels Uzbek via `labels.ts`

**Verification:**
- [ ] Manual: search "madaniyat", apply year filter, click result → lands on correct doc
- [ ] URL persists state — refresh keeps filters
- [ ] No regression on existing `/archive/[year]` table

**Dependencies:** 7.2
**Files likely touched:** 1 new + 1 labels edit
**Estimated scope:** L

---

### Task 7.4: Global search box in dashboard header

**Description:** Add a search input to `layouts/dashboard.vue` header (top bar).
Enter / click → navigates to `/archive/search?q=…`. Visible on every dashboard page.

**Acceptance criteria:**
- [ ] Input in header, icon `i-lucide-search`, placeholder "Hujjatlarda qidirish…"
- [ ] Enter or icon-click navigates to `/archive/search?q=…`
- [ ] Keyboard shortcut: `/` focuses the input (skip if focus is already in an input)
- [ ] Mobile: collapses to icon-only

**Verification:**
- [ ] From any dashboard page, type "test" → Enter → lands on search page with q="test"

**Dependencies:** 7.3
**Files likely touched:** 1 (dashboard.vue)
**Estimated scope:** S

---

### Checkpoint: After Phase 7

- [ ] Advanced search page works with all filter combinations
- [ ] Highlights render correctly with `<mark>` wrapping
- [ ] Facet counts are accurate
- [ ] Global search box works from every dashboard page
- [ ] No regression on existing flows
- [ ] Commit Phase 7
- [ ] **Human review before release**

---

## Parallelization Opportunities

- Phases 4 → 5 → 6 → 7 must run sequentially (each depends on the previous).
- **Within Phase 4**: 4.2 and 4.4 can run in parallel after 4.1.
- **Within Phase 5**: 5.5 (CLI) and 5.6 (health) can run in parallel after 5.4.
- **Within Phase 6**: 6.4 (backfill CLI) and 6.5 (UI badges) can run in parallel after 6.3.
- **Within Phase 7**: 7.4 (header search) can be done by a second agent in parallel with
  7.3 (search page).

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Tesseract Uzbek accuracy on Cyrillic + Latin mixed docs is uneven | High | Med | Phase 6.1 tries both `uzb` and `uzb_cyrl`, keeps longer result. Add `--lang` override env var. Accept that some docs need manual review (`ocr_status=failed` is OK — they remain searchable by metadata). |
| ES memory: 1GB heap per container is borderline for a Ministry-scale archive | Med | Med | Single-node is enough for ≤500k docs. Document the upgrade path: bump heap, then add nodes. Monitor with Kibana. |
| arq queue backs up if a job loop crashes the worker | Med | High | Worker restarts (Docker `restart: unless-stopped`). Outbox table acts as durable retry buffer — nothing is lost. Add Prometheus / log alert on queue depth > 1000 in a future phase. |
| Data migration script misses an FK relationship | Low | High | Add `--verify` step that re-counts every table after migration. Manual smoke test of golden flows (login, list, create, edit, delete) before declaring done. |
| ES `documents` alias changes break search during reindex | Low | Med | Use the alias-swap pattern: build `documents-v2`, populate, then atomically swap alias. (Phase 5 doesn't need this yet, but the alias is in place from 5.1.) |
| Concurrent edits during phase-6 backfill cause stale OCR text | Low | Low | OCR job writes only `extracted_text` + status; never touches metadata. Worst case: doc is reindexed twice. |
| Tesseract OS-level dep on Windows dev | High | Low | Docker the worker (Dockerfile.worker installs `tesseract-ocr` + `tesseract-ocr-uzb` + `poppler-utils`). Native Windows install also works via chocolatey but documented as fallback. |
| Frontend `v-html` of ES highlights | Low | Med | ES emits only `<mark>` tags around indexed tokens; no user-controllable HTML reaches the output. Add unit-test of the renderer to confirm. |
| Postgres prod DB has data the SQLite migration doesn't anticipate | Low | High | Make migration script `--dry-run`-able with row count diff before commit. Run against a Postgres copy before pointing prod at it. |

## Open Questions

1. **Authentication for search** — currently locked as "any logged-in user". Confirm
   if certain document_views (e.g. internal) should require additional permissions.
   Default: no, search reflects what list APIs already return.
2. **Result ranking weights** — `title^3, document_number^3, short_desc^2,
   extracted_text^1` — adjust after Phase 7 ships and we see real query patterns.
3. **Retention of OCR text on document delete** — locked as "deleted along with the
   document" (cascade via FK). Confirm if compliance requires keeping the text in a
   tombstone table.

## Verification (pre-implementation)

- [x] Every task has acceptance criteria
- [x] Every task has a verification step
- [x] Task dependencies identified and ordered
- [x] Vertical slicing — each phase delivers user-visible value (except Phase 4 which is
      foundational and explicitly checkpointed as such)
- [x] Tech defaults locked to avoid 20 round-trips
- [x] Checkpoints between phases
- [x] Human has reviewed and approved this plan
