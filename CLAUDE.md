# Document Archive Platform - Madaniyat vazirligi Arxiv tizimi

## Project Overview

Archive system for the Ministry of Culture of Uzbekistan. Documents organized by year and category, with dynamic fields per category.

## Tech Stack

- **Backend**: Python 3.13 + FastAPI + SQLAlchemy (async) + Alembic
- **Frontend**: Nuxt 3 (v4 compat) + @nuxt/ui v3 + Tailwind CSS + Zod
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Auth**: JWT (username/password), bcrypt for hashing
- **Package managers**: `uv` (Python), `npm` (frontend)

## Architecture

Backend follows DDD (Domain-Driven Design):
```
backend/src/
  domain/       # Entities, value objects, repository interfaces (no deps)
  application/  # Commands, queries, handlers (depends on domain)
  infrastructure/ # SQLAlchemy repos, auth, file storage (implements domain)
  api/          # FastAPI routes, schemas, middleware (entry point)
```

## Running

```bash
# Backend
cd backend
uv venv .venv && uv pip install -e .
uv run alembic upgrade head
uv run uvicorn src.api.main:app --reload  # http://localhost:8000

# Frontend
cd frontend
npm install
npm run dev  # http://localhost:3000
```

## Default credentials

- Username: `admin`, Password: `admin123`

## Key Decisions

- **No @nuxt/ui-pro**: Dashboard components (UDashboardPanel, etc.) are pro-only. Using custom `PagePanel` and `EmptyState` components instead.
- **SQLite compat**: Models use custom `GUID` type (CHAR(36)) instead of PostgreSQL UUID, and `JSON` instead of `JSONB`. Alembic env handles both sync (SQLite) and async (PostgreSQL).
- **No passlib**: Incompatible with newer bcrypt. Using `bcrypt` library directly via `src/infrastructure/auth/password_service.py`.
- **Dynamic fields**: EAV pattern — `category_fields` defines schemas, `document_field_values` stores data. Common document fields are real columns.
- **Nuxt UI v3 UTable**: Uses TanStack Table — columns need `accessorKey`/`header` (not `key`/`label`). Empty-header columns need explicit `id`.
- **Pydantic schemas**: Do NOT use `from __future__ import annotations` — breaks Pydantic type evaluation. Use `import datetime as dt` to avoid field name shadowing.

## API Base

- Backend: `http://localhost:8000/api`
- Frontend proxies via `runtimeConfig.public.apiBase`

## Database

- Dev: `sqlite+aiosqlite:///./arxiv_db.db` (in backend/)
- Prod: `postgresql+asyncpg://...`
- Migrations: `cd backend && uv run alembic revision --autogenerate -m "description"` then `uv run alembic upgrade head`
- Alembic autogenerate writes `GUID` as `src.infrastructure...GUID(length=36)` — manually replace with `sa.String(length=36)` in migration files.

## Frontend Structure

```
frontend/app/
  layouts/      # auth.vue (login), dashboard.vue (sidebar), default.vue
  pages/        # File-based routing
  components/   # PagePanel, EmptyState, document/DocumentForm, document/DocumentFieldRenderer
  composables/  # useAuth, useDocuments
  utils/        # api.ts (auth fetch), buildFieldSchema.ts (dynamic Zod)
  types/        # TypeScript interfaces
```

## Route Map

```
/login                                    # Username/password
/archive                                  # Year grid
/archive/:year                            # Category cards
/archive/:year/:categoryId                # Documents table + search
/archive/:year/:categoryId/create         # Create document (dynamic form)
/archive/:year/:categoryId/:id            # Document detail
/archive/:year/:categoryId/:id/edit       # Edit document
/admin/users                              # Users CRUD (admin only)
/admin/years                              # Years CRUD (admin only)
/admin/categories                         # Categories CRUD (admin only)
/admin/categories/:id/fields              # Category field management
```

## Theme

Primary color: `#043B87` (ministry blue) — defined as `madaniyat` in `app/assets/css/main.css` and set as `primary` in `app/app.config.ts`. All UI labels in Uzbek.
