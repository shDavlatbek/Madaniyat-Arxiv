"""Lazy singleton accessor for the async Elasticsearch client.

The client is constructed on first access and reused across requests. Callers
that need to invalidate (e.g. tests) can call :func:`close_es`.
"""
from __future__ import annotations

from elasticsearch import AsyncElasticsearch

from src.infrastructure.config import settings

_client: AsyncElasticsearch | None = None


def get_es() -> AsyncElasticsearch:
    global _client
    if _client is None:
        _client = AsyncElasticsearch(
            hosts=[settings.elasticsearch_url],
            request_timeout=10,
        )
    return _client


async def close_es() -> None:
    global _client
    if _client is not None:
        await _client.close()
        _client = None
