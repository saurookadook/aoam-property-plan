from __future__ import annotations

from typing import Annotated, Any, Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from db.db_session_manager import DBSessionManager

DBSessionGenerator = Generator[Session, Any, None]


def db_session() -> DBSessionGenerator:
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


DBSessionDependency = Annotated[DBSessionGenerator, Depends(db_session)]
