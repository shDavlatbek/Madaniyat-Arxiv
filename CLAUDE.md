# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Archive system for the Ministry of Culture of Uzbekistan (Madaniyat vazirligi Arxiv tizimi). Documents organized by year and category, with dynamic fields per category. Each category belongs to one year. When creating a new year, categories can be imported (copied) from an existing year.

## Tech Stack

- **Backend**: Python 3.13 + FastAPI + SQLAlchemy (async) + Alembic
- **Frontend**: Nuxt 4 + @nuxt/ui v4 + Tailwind CSS v4 + Zod
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Auth**: JWT (username/password), bcrypt for hashing
- **Package managers**: `uv` (Python), `npm` (frontend)

## Commands

```bash
# Backend
cd backend
uv venv .venv && uv pip install -e .
uv run alembic upgrade head
uv run uvicorn src.api.main:app --reload        # http://localhost:8000

# Frontend
cd frontend
npm install
npm run dev                                      # http://localhost:3000
npm run build                                    # production build

# Database migrations
cd backend
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
```

Default credentials: `admin` / `admin123`

## Architecture

Backend follows DDD (Domain-Driven Design):
```
backend/src/
  domain/         # Entities, value objects, repository interfaces (no external deps)
  application/    # Commands, queries, handlers (depends on domain only)
  infrastructure/ # SQLAlchemy repos, auth, file storage (implements domain interfaces)
  api/            # FastAPI routes, Pydantic schemas, middleware (entry point)
```

Frontend:
```
frontend/app/
  layouts/        # auth.vue (login), dashboard.vue (sidebar nav + user menu)
  pages/          # File-based routing
  components/     # PagePanel, EmptyState, DatePicker, document/*
  composables/    # useAuth, useDocuments, useApi
  utils/          # api.ts (auth fetch wrapper)
  types/          # TypeScript interfaces
```

## Key Gotchas

- **Pydantic schemas**: Do NOT use `from __future__ import annotations` — breaks Pydantic type evaluation at runtime.
- **UTable (TanStack Table v3)**: Columns use `accessorKey`/`header` (not `key`/`label`). Empty-header columns need explicit `id`. Cell slot data accessed via `row.original.*` (not `row.*`).
- **find_by_year()**: The `year_id` parameter is the year VALUE (e.g. 2020), not the DB primary key. Repository joins `YearModel` to match by `YearModel.value`.
- **SQLite compat**: Models use custom `GUID` type (CHAR(36)) instead of PostgreSQL UUID, and `JSON` instead of `JSONB`. Alembic autogenerate writes `GUID` as `src.infrastructure...GUID(length=36)` — manually replace with `sa.String(length=36)` in migration files.
- **No passlib**: Incompatible with newer bcrypt. Using `bcrypt` library directly via `src/infrastructure/auth/password_service.py`.
- **CORS origins**: Hardcoded in `backend/src/api/main.py` — update when deploying or changing frontend port.
- **Color mode**: Forced to `light` in `nuxt.config.ts` (`colorMode.preference` and `fallback`).

## Domain Patterns

- **Category-Year relationship**: Each category has a single `year_id` FK. `import_from_year_id` on year creation copies categories with all fields as new records.
- **Default field templates**: `default_fields` table stores admin-managed templates. Auto-copied as initial category fields when creating a category. Admin page at `/admin/default-fields`.
- **Copy category**: `POST /api/categories/{id}/copy` with `{ target_year_id }` duplicates a category (name/code/fields) into the target year.
- **Dynamic fields (EAV)**: `category_fields` defines field schemas per category, `document_field_values` stores per-document data. Common document fields (title, date, etc.) are real columns.
- **File upload**: Two-step — create document first, then `POST /api/documents/{id}/file` with FormData. Download uses authenticated `fetch()` + blob URL (JWT required).
- **PDF viewer**: Uses `pdfjs-dist` with authenticated fetch (blob URL) since file API requires JWT.
- **DatePicker**: `UInputDate` + `UPopover` + `UCalendar` from Nuxt UI v4. Converts between `YYYY-MM-DD` string (backend) and `CalendarDate` (frontend).

## API

- Backend base: `http://localhost:8000/api`
- Frontend proxies via `runtimeConfig.public.apiBase` in `nuxt.config.ts`
- Database: `sqlite+aiosqlite:///./arxiv_db.db` (dev), `postgresql+asyncpg://...` (prod)

## Route Map

```
/login                                    # Username/password
/archive                                  # Year grid
/archive/:year                            # Documents table + category/date filter + field search
/archive/:year/:categoryId/create         # Create document (dynamic form + file upload)
/archive/:year/:categoryId/:id            # Document detail (PDF preview + details)
/archive/:year/:categoryId/:id/edit       # Edit document
/admin/users                              # Users CRUD (admin only)
/admin/years                              # Years CRUD + import categories
/admin/categories                         # Categories CRUD + copy
/admin/categories/:id/fields              # Category field management
/admin/default-fields                     # Default field templates
```

## API Endpoints

```
POST   /api/auth/login
GET    /api/auth/me

GET|POST        /api/users
GET|PUT|DELETE  /api/users/:id
PUT             /api/users/:id/password

GET|POST        /api/years                     # GET: ?active_only=true
PUT|DELETE      /api/years/:id
                                               # POST body: { value, is_active, import_from_year_id? }

GET|POST        /api/categories                # POST: { name, code, year_id, description?, sort_order? }
PUT|DELETE      /api/categories/:id
POST            /api/categories/:id/copy       # { target_year_id }
GET             /api/years/:yearValue/categories

GET|POST        /api/categories/:id/fields
PUT|DELETE      /api/categories/:id/fields/:fieldId

GET|POST        /api/default-fields
PUT|DELETE      /api/default-fields/:id

GET|POST        /api/documents                 # GET: ?year_id&category_id&search&date_from&date_to&field_filters&page&page_size
GET|PUT|DELETE  /api/documents/:id
POST            /api/documents/:id/file        # upload (FormData)
GET             /api/documents/:id/file        # download
```

## Theme

Primary color: `#043B87` (ministry blue) — defined as `madaniyat` in `app/assets/css/main.css` and set as `primary` in `app/app.config.ts`. All UI labels in Uzbek.
