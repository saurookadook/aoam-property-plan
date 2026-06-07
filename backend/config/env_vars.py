from __future__ import annotations

import os
from typing_extensions import Self

from pydantic import BaseModel, Field, model_validator


class EnvVars(BaseModel):
    airroi_api_key: str = Field(
        default_factory=lambda: os.getenv("AIRROI_API_KEY", default="UNSET")
    )
    base_domain: str = Field(
        default_factory=lambda: os.getenv("BASE_DOMAIN", default="aoam.dev")
    )
    base_api_url: str = Field(default="UNSET")
    base_app_url: str = Field(default="UNSET")

    csrf_secret: str = Field(default_factory=lambda: os.getenv("CSRF_SECRET", "TMP"))
    database_user: str = Field(
        default_factory=lambda: os.getenv("DATABASE_USER", "postgres")
    )
    database_password: str = Field(
        default_factory=lambda: os.getenv("DATABASE_PASSWORD", "example")
    )
    database_host: str = Field(
        default_factory=lambda: os.getenv("DATABASE_HOST", "pg_database")
    )
    database_port: int = Field(
        default_factory=lambda: int(os.getenv("DATABASE_PORT", "5432"))
    )
    database_name: str = Field(
        default_factory=lambda: os.getenv("DATABASE_NAME", "aoam_property_plan")
    )
    env: str = Field(default_factory=lambda: os.getenv("ENV", "dev"))
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "DEBUG"))
    log_sql: bool = Field(default_factory=lambda: EnvVars._parse_bool("LOG_SQL", False))
    """
    Valid values: `true`, `false`, `1`, `0`, `yes`, `no` (case insensitive)
    """

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
        # TODO: properly validate ``base_domain``
        setattr(self, "base_api_url", f"https://{self.base_domain}/api")
        setattr(self, "base_app_url", f"https://{self.base_domain}/app")
        return self

    @classmethod
    def _parse_bool(cls, key: str, fallback_value: bool) -> bool:
        value = os.getenv(key, str(fallback_value))
        return value.lower() in ("true", "1", "yes")
