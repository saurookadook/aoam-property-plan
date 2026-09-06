from __future__ import annotations

from typing import Annotated, Any, Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from db.db_session_manager import DBSessionManager

DBSessionGenerator = Generator[Session, Any, None]


def db_session_generator() -> DBSessionGenerator:
    """FastAPI dependency to get database session

    Built from the session factory rather than from ``scoped_session``, and
    closed by object rather than by ``scoped_session.remove()``. ``remove()``
    resolves the registry entry for *the calling thread*, and FastAPI does not
    run a sync dependency's setup and teardown on the same thread: ``__enter__``
    goes through the shared threadpool, ``__exit__`` through
    ``anyio.to_thread.run_sync`` under its own limiter. So ``remove()`` here
    would close whichever session the teardown thread happened to hold - another
    in-flight request's, mid-``commit()`` - while this request's own session was
    left in the setup thread's registry forever.

    Yields:
        Session: open database session
    """
    session = DBSessionManager().scoped_session.session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def api_db_session() -> DBSessionGenerator:
    yield from db_session_generator()


API_DB_SessionDependency = Annotated[Session, Depends(api_db_session)]
