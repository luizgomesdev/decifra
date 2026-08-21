"""Postgres-backed conversation memory.

The agent's own checkpointer is the store: LangGraph persists the message list
per thread, so conversation history survives a restart without a schema of our
own. One thread per conversation session. The patient id is part of the thread id so
the isolation the retrieval filter provides is mirrored in the memory, and a
patient can have more than one conversation instead of a single endless one.

`from_conn_string` is a context manager meant for short-lived use. A long-lived
server wants a pool, so the saver is built once over a ConnectionPool and kept.
"""

from functools import lru_cache
from uuid import uuid4

from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool

from decifra.config import get_settings


def _psycopg_dsn() -> str:
    """SQLAlchemy-style URL to plain libpq DSN, which psycopg expects."""
    return get_settings().database_url.replace("postgresql+psycopg://", "postgresql://")


@lru_cache
def get_pool() -> ConnectionPool:
    pool = ConnectionPool(
        conninfo=_psycopg_dsn(),
        min_size=1,
        max_size=10,
        kwargs={"autocommit": True, "prepare_threshold": 0},
        open=True,
    )
    return pool


@lru_cache
def get_checkpointer() -> PostgresSaver:
    saver = PostgresSaver(get_pool())
    saver.setup()
    return saver


def thread_id_for(patient_id: str, session_id: str) -> str:
    return f"{patient_id}:{session_id}"


def new_session_id() -> str:
    return uuid4().hex[:12]


def close_pool() -> None:
    """Called on shutdown. Without it psycopg logs stuck worker threads."""
    if get_pool.cache_info().currsize:
        get_pool().close()
