.PHONY: backend frontend dev install migrate migration

# Run both backend and frontend concurrently
dev:
	$(MAKE) backend & $(MAKE) frontend & wait

# Backend
backend:
	cd backend && .\.venv\Scripts\activate && uv run uvicorn src.api.main:app --reload

# Frontend
frontend:
	cd frontend && npm run dev

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
