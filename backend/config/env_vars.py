from __future__ import annotations

import os
from typing_extensions import Self

from pydantic import Field, model_validator

from backend.utils.pydantic_helpers import BaseModel


class EnvVars(BaseModel):
    base_domain: str = Field(
        default_factory=lambda: os.getenv("BASE_DOMAIN", default="aoam.dev")
    )

    csrf_secret: str = Field(default_factory=lambda: os.getenv("CSRF_SECRET", "TMP"))
    database_user: str = Field(
        default_factory=lambda: os.getenv("DATABASE_USER", "postgres")
    )
    database_password: str = Field(
        default_factory=lambda: os.getenv("DATABASE_PASSWORD", "example")
    )
    database_host: str = Field(
        default_factory=lambda: os.getenv("DATABASE_HOST", "database")
    )
    database_port: int = Field(
        default_factory=lambda: int(os.getenv("DATABASE_PORT", "5432"))
    )
    database_name: str = Field(
        default_factory=lambda: os.getenv("DATABASE_NAME", "the_money_maker")
    )
    env: str = Field(default_factory=lambda: os.getenv("ENV", "dev"))
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "DEBUG"))
    log_sql: bool = Field(default_factory=lambda: bool(os.getenv("LOG_SQL", False)))

    # Auth
    auth_cookie_key: str = Field(
        default_factory=lambda: os.getenv(
            "AUTH_COOKIE_KEY", default="AOAM-Authorization.Dev"
        )
    )
    github_oauth_client_id: str = Field(
        default_factory=lambda: os.getenv("GITHUB_OAUTH_CLIENT_ID", default="")
    )
    github_oauth_client_secret: str = Field(
        default_factory=lambda: os.getenv("GITHUB_OAUTH_CLIENT_SECRET", default="")
    )
    github_oauth_callback_url: str = Field(
        default_factory=lambda: os.getenv("GITHUB_OAUTH_CALLBACK_URL", default="")
    )
    github_oauth_auth_url: str = Field(
        default_factory=lambda: "https://github.com/login/oauth/authorize"
    )
    github_oauth_token_url: str = Field(
        default_factory=lambda: "https://github.com/login/oauth/access_token"
    )
    github_oauth_scopes: list[str] = Field(default_factory=lambda: [])

    # Session Cache
    memcached_host: str = Field(
        default_factory=lambda: os.getenv("MEMCACHED_HOST", default="memcached")
    )
    memcached_port: int = Field(
        default_factory=lambda: int(os.getenv("MEMCACHED_PORT", default="11211"))
    )

    @model_validator(mode="after")
    def post_init_hook(self) -> Self:
        # TODO: properly validate BASE_DOMAIN
        setattr(self, "BASE_API_URL", f"https://{self.BASE_DOMAIN}/api")
        setattr(self, "BASE_APP_URL", f"https://{self.BASE_DOMAIN}/app")
        return self
