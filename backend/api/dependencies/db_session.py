from __future__ import annotations

from db.db_session_manager import DBSessionManager


def db_session():
    """FastAPI dependency to get database session

    Yields:
        Session: open database session
    """
    session = DBSessionManager().scoped_session
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
