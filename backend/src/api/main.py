import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.domain.shared.errors import AuthorizationError, DomainError, NotFoundError, ValidationError
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


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
