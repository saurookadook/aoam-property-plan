from __future__ import annotations

from sqlalchemy.orm import Session, scoped_session

from db.db_session_manager import DBSessionManager


class BaseFacade:
    def __init__(self, *, db_session: scoped_session[Session] | None = None):
        self.db_session = (
            db_session if db_session is not None else DBSessionManager().scoped_session
        )
