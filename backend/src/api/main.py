import asyncio
import logging
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from src.domain.shared.errors import AuthorizationError, DomainError, NotFoundError, ValidationError
from src.infrastructure.jobs.arq_pool import close_arq_pool
from src.infrastructure.persistence.database import async_session
from src.infrastructure.search.es_client import close_es, get_es
from src.infrastructure.search.index_template import ensure_index

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure the Elasticsearch index + alias exist before serving traffic.
    # A transient ES outage on boot is logged but not fatal — the app stays
    # available for non-search endpoints, and the next request that needs ES
    # surfaces the underlying error.
    try:
        await ensure_index(get_es())
    except Exception as exc:  # noqa: BLE001
        log.warning("ensure_index failed on startup: %s", exc)
    yield
    await close_es()
    await close_arq_pool()


app = FastAPI(
    title="Arxiv API",
    description="Document Archive Platform - Madaniyat vazirligi",
    version="0.1.0",
    lifespan=lifespan,
)

from src.infrastructure.config import settings as app_settings

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in app_settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": exc.message})


@app.exception_handler(ValidationError)
async def validation_handler(request: Request, exc: ValidationError):
    return JSONResponse(status_code=400, content={"detail": exc.message})


@app.exception_handler(AuthorizationError)
async def authorization_handler(request: Request, exc: AuthorizationError):
    return JSONResponse(status_code=403, content={"detail": exc.message})


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse(status_code=400, content={"detail": exc.message})


# Routes
from src.api.routes.auth_routes import router as auth_router
from src.api.routes.user_routes import router as user_router
from src.api.routes.year_routes import router as year_router
from src.api.routes.category_routes import router as category_router
from src.api.routes.document_routes import router as document_router
from src.api.routes.person_routes import router as person_router
from src.api.routes.department_routes import router as department_router
from src.api.routes.archive_folder_routes import router as archive_folder_router
from src.api.routes.document_type_routes import router as document_type_router
from src.api.routes.reference_routes import router as reference_router

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(year_router)
app.include_router(category_router)
app.include_router(document_router)
app.include_router(person_router)
app.include_router(department_router)
app.include_router(archive_folder_router)
app.include_router(document_type_router)
app.include_router(reference_router)


async def _check_postgres() -> bool:
    try:
        async with async_session() as s:
            await asyncio.wait_for(s.execute(text("SELECT 1")), timeout=1.0)
        return True
    except Exception as exc:  # noqa: BLE001
        log.warning("health: postgres down — %s", exc)
        return False


async def _check_elasticsearch() -> bool:
    try:
        await asyncio.wait_for(get_es().cluster.health(), timeout=1.0)
        return True
    except Exception as exc:  # noqa: BLE001
        log.warning("health: elasticsearch down — %s", exc)
        return False


async def _check_redis() -> bool:
    client = aioredis.from_url(app_settings.redis_url, socket_connect_timeout=1)
    try:
        await asyncio.wait_for(client.ping(), timeout=1.0)
        return True
    except Exception as exc:  # noqa: BLE001
        log.warning("health: redis down — %s", exc)
        return False
    finally:
        await client.aclose()


@app.get("/api/health")
async def health_check():
    pg_ok, es_ok, redis_ok = await asyncio.gather(
        _check_postgres(), _check_elasticsearch(), _check_redis()
    )
    body = {
        "status": "ok" if (pg_ok and es_ok and redis_ok) else "degraded",
        "postgres": "ok" if pg_ok else "down",
        "elasticsearch": "ok" if es_ok else "down",
        "redis": "ok" if redis_ok else "down",
    }
    status_code = 200 if body["status"] == "ok" else 503
    return JSONResponse(content=body, status_code=status_code)
