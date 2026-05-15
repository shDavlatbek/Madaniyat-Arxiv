"""arq worker bootstrap.

Phase 4.4 ships the runtime only — the Redis-backed task queue process — with
a single placeholder ``health_check`` job. Real jobs land in later phases:
the document indexer drains the ``search_index_jobs`` outbox to Elasticsearch
(Phase 5.4), and the OCR pipeline extracts text from uploaded files (Phase 6.3).

Run with::

    uv run arq src.infrastructure.jobs.worker.WorkerSettings

or via ``make worker``.
"""
from __future__ import annotations

import logging
from urllib.parse import urlparse

from arq.connections import RedisSettings

from src.infrastructure.config import settings

log = logging.getLogger("worker")


def _redis_settings_from_url(url: str) -> RedisSettings:
    """Parse a ``redis://host:port/db`` URL into ``RedisSettings``."""
    parsed = urlparse(url)
    return RedisSettings(
        host=parsed.hostname or "localhost",
        port=parsed.port or 6379,
        database=int(parsed.path.lstrip("/") or "0"),
        password=parsed.password,
    )


async def health_check(ctx: dict) -> str:
    """Placeholder job — enqueue this to prove the worker is alive."""
    log.info("health_check: ok (job_id=%s)", ctx.get("job_id"))
    return "ok"


async def startup(ctx: dict) -> None:
    log.info("worker startup: redis=%s", settings.redis_url)


async def shutdown(ctx: dict) -> None:
    log.info("worker shutdown")


class WorkerSettings:
    """arq picks this up by reference; see https://arq-docs.helpmanual.io/."""

    functions = [health_check]
    redis_settings = _redis_settings_from_url(settings.redis_url)
    on_startup = startup
    on_shutdown = shutdown
