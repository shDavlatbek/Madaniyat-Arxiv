from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.domain.shared.errors import AuthorizationError, DomainError, NotFoundError, ValidationError


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Arxiv API",
    description="Document Archive Platform - Madaniyat vazirligi",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://192.168.20.196:3000"],
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

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(year_router)
app.include_router(category_router)
app.include_router(document_router)
app.include_router(person_router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
