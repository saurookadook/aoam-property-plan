from __future__ import annotations

from typing import Optional

from sqlalchemy import Dialect, Engine, create_engine, TIMESTAMP
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import (
    Mapped,
    as_declarative,
    declared_attr,
    mapped_column,
    sessionmaker,
    scoped_session,
)

from config.env_var_manager import EnvVarManager
from utils.singleton_meta import SingletonMeta

env_vars = EnvVarManager().env_vars

# engine = create_engine(
#     f"postgresql+psycopg2://{env_vars.database_user}:{env_vars.database_password}"
#     f"@{env_vars.database_host}:{env_vars.database_port}/{env_vars.database_name}",
#     echo=env_vars.log_sql,
#     max_overflow=30,
#     connect_args={"options": "-c timezone=utc"},
#     future=True,
# )


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

        if not hasattr(self, "SessionFactory"):
            self.SessionFactory = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine, future=True
            )
        if not hasattr(self, "ScopedSession"):
            self.ScopedSession = scoped_session(self.SessionFactory)

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
            echo=log_sql,
            max_overflow=30,
            connect_args={"options": "-c timezone=utc"},
            future=True,
        )
