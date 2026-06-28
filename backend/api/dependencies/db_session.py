from __future__ import annotations

from typing import Annotated, Any, Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from db.db_session_manager import DBSessionManager

DBSessionGenerator = Generator[Session, Any, None]


def db_session_generator() -> DBSessionGenerator:
    """FastAPI dependency to get database session

    Yields:
        Session: open database session
    """
    session = DBSessionManager().scoped_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        DBSessionManager().scoped_session.remove()


def api_db_session() -> DBSessionGenerator:
    yield from db_session_generator()


API_DB_SessionDependency = Annotated[Session, Depends(api_db_session)]
