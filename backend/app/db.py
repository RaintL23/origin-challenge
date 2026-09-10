from __future__ import annotations

from functools import lru_cache

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.config import Settings, get_settings


@lru_cache
def get_pool(database_url: str) -> ConnectionPool:
    return ConnectionPool(
        conninfo=database_url,
        min_size=1,
        max_size=10,
        kwargs={"row_factory": dict_row},
        open=True,
    )


def get_connection_pool(settings: Settings | None = None) -> ConnectionPool:
    cfg = settings or get_settings()
    return get_pool(cfg.database_url)


def close_connection_pool() -> None:
    database_url = get_settings().database_url
    pool = get_pool(database_url)
    pool.close()
    get_pool.cache_clear()
