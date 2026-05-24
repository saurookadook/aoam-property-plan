from __future__ import annotations

from typing import Optional

from sqlalchemy import Engine, create_engine
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import sessionmaker, scoped_session

from config.env_var_manager import EnvVarManager
from utils.singleton_meta import SingletonMeta

env_vars = EnvVarManager().env_vars


class DBSessionManager(metaclass=SingletonMeta):
    def __init__(self, engine: Optional[Engine] = None):
        if engine is not None or not hasattr(self, "engine"):
            self.engine = (
                engine
                if engine is not None
                else DBSessionManager.create_psql_engine(
                    database=env_vars.database_name,
                    host=env_vars.database_host,
                    password=env_vars.database_password,
                    port=env_vars.database_port,
                    user=env_vars.database_user,
                )
            )

        if not hasattr(self, "session_factory"):
            self.session_factory = lambda: sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine, future=True
            )
        if not hasattr(self, "scoped_session"):
            self.scoped_session = scoped_session(self.session_factory())

    @classmethod
    def build_psql_url(cls, **kwargs) -> str:
        env_vars = EnvVarManager().env_vars
        database = (
            kwargs["database"] if "database" in kwargs else env_vars.database_name
        )
        host = kwargs["host"] if "host" in kwargs else env_vars.database_host
        password = (
            kwargs["password"] if "password" in kwargs else env_vars.database_password
        )
        port = kwargs["port"] if "port" in kwargs else env_vars.database_port
        user = kwargs["user"] if "user" in kwargs else env_vars.database_user

        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

    @classmethod
    def create_psql_engine(cls, **kwargs) -> Engine:
        env_vars = EnvVarManager().env_vars
        log_sql = kwargs["log_sql"] if "log_sql" in kwargs else env_vars.log_sql

        return create_engine(
            cls.build_psql_url(**kwargs),
            connect_args={"options": "-c timezone=utc"},
            echo=log_sql,
            future=True,
            max_overflow=30,
            plugins=["geoalchemy2"],
        )
