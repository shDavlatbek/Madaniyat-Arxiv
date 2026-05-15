# Arxiv — Madaniyat vazirligi Arxiv tizimi

Document archive platform for the Ministry of Culture of Uzbekistan.

- **Backend**: Python 3.13 + FastAPI + SQLAlchemy (async) + Alembic
- **Frontend**: Nuxt 4 + @nuxt/ui v4 + Tailwind CSS v4
- **Database**: PostgreSQL 16 (SQLite supported for legacy dev)
- **Search**: Elasticsearch 8.x (Phase 5+)
- **Queue**: Redis 7 + `arq` (Phase 5+)

See [CLAUDE.md](CLAUDE.md) for architecture, conventions, and gotchas.

## Local dev stack

The repo ships with `docker-compose.yml` configured around two compose profiles:

| Profile | Services started | Use case |
|---------|------------------|----------|
| _(default)_ | `db`, `redis`, `elasticsearch` | **Dev**: run backend + frontend natively, dockerize only infra |
| `app` | + `backend`, `frontend` | Full prod-style stack inside docker |
| `tools` | + `kibana` | ES debugging at <http://localhost:5601> |

### One-time setup

1. Install Docker Desktop.
2. Copy env files:
   ```sh
   cp .env.example .env
   cp backend/.env.example backend/.env
   ```
3. (Linux only) raise the kernel limit Elasticsearch requires:
   ```sh
   sudo sysctl -w vm.max_map_count=262144
   ```
   On Docker Desktop (macOS / Windows) this is handled automatically.

### Day-to-day: dev mode

```sh
# Start infra (postgres + redis + elasticsearch)
docker compose up -d

# Run backend + frontend natively
make dev          # opens two Windows Terminal tabs
# or, separately:
make backend
make frontend
```

Open the dashboard at <http://localhost:3000>.

### Full docker stack

```sh
docker compose --profile app up -d
```

### With Kibana for ES debugging

```sh
docker compose --profile tools up -d kibana
```

### Verify the stack

```sh
# Postgres
psql postgresql://postgres:postgres@localhost:5432/arxiv_db -c '\l'

# Elasticsearch
curl http://localhost:9200

# Redis
docker compose exec redis redis-cli ping
```

### Stop / reset

```sh
docker compose down               # stop containers, keep data
docker compose down -v            # also wipe volumes (postgres, redis, es, uploads)
```

## Running migrations

```sh
make migrate                      # apply pending migrations
make migration m="add foo table"  # autogenerate a new revision
```

## Project layout

```
backend/             FastAPI + DDD layered architecture
  src/
    domain/          Entities, value objects, repository interfaces
    application/     Commands, queries, handlers
    infrastructure/  SQLAlchemy, auth, file storage, search (Phase 5+)
    api/             FastAPI routes, schemas, middleware
  alembic/           Database migrations
  scripts/           One-shot CLIs (data migration, reindex, OCR backfill)

frontend/            Nuxt 4 SPA
  app/
    layouts/         auth.vue, dashboard.vue
    pages/           File-based routing
    components/      Shared components
    composables/     useAuth, useDocuments, useApi, useSearch
    utils/           api.ts, labels.ts

tasks/               plan.md + todo.md — the source of truth for what's
                     being built and what's next
```
