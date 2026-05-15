"""Lazy singleton accessor for the arq Redis pool.

FastAPI routes enqueue background work (OCR, future reindex triggers)
through this pool. The pool itself is shared across the process and torn
down in the app's lifespan.
"""
from __future__ import annotations

from arq import create_pool
from arq.connections import ArqRedis

from src.infrastructure.jobs.worker import WorkerSettings

_pool: ArqRedis | None = None


async def get_arq_pool() -> ArqRedis:
    global _pool
    if _pool is None:
        _pool = await create_pool(WorkerSettings.redis_settings)
    return _pool


async def close_arq_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.aclose()
        _pool = None
