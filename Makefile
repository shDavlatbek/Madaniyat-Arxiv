.PHONY: backend frontend worker dev install migrate migration

# Run both backend and frontend concurrently in separate windows
# Run both backend and frontend concurrently in separate tabs (Windows Terminal only)
dev:
	wt -w 0 nt -d . cmd /k "make backend"
	wt -w 0 nt -d . cmd /k "make frontend"

# Backend
backend:
	cd backend && uv run uvicorn src.api.main:app --reload --host 0.0.0.0

# Frontend
frontend:
	cd frontend && npx nuxi dev --host 0.0.0.0

# Background task worker (arq + Redis)
worker:
	cd backend && uv run arq src.infrastructure.jobs.worker.WorkerSettings

# Install all dependencies
install:
	cd backend && uv venv .venv && uv pip install -e .
	cd frontend && npm install

# Run pending migrations
migrate:
	cd backend && uv run alembic upgrade head

# Create a new migration (usage: make migration m="description")
migration:
	cd backend && uv run alembic revision --autogenerate -m "$(m)"