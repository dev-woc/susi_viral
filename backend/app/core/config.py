from __future__ import annotations

from functools import lru_cache
from os import getenv
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Runtime configuration for the backend scaffold."""

    app_name: str = "viral-content-agent-backend"
    api_prefix: str = "/api"
    database_url: str = "sqlite:///./viral_content_agent.db"
    redis_url: str = "redis://localhost:6379/0"
    log_level: str = "INFO"
    database_echo: bool = False
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-sonnet-latest"
    default_workspace_slug: str = "personal"
    default_workspace_name: str = "Personal Workspace"
    default_user_external_id: str = "demo-user"
    default_user_email: str = "demo@example.com"
    default_user_display_name: str = "Demo User"
    search_result_limit: int = Field(default=10, ge=1, le=50)
    extraction_result_limit: int = Field(default=10, ge=1, le=50)
    connector_clip_limit: int = Field(default=6, ge=1, le=20)
    enable_mock_connectors: bool = True
    enable_mock_extraction: bool = True

    @property
    def has_anthropic_credentials(self) -> bool:
        return bool(self.anthropic_api_key)


def load_settings() -> Settings:
    """Load settings from the environment with sane local defaults."""

    return Settings(
        app_name=getenv("APP_NAME", "viral-content-agent-backend"),
        api_prefix=getenv("API_PREFIX", "/api"),
        database_url=getenv("DATABASE_URL", "sqlite:///./viral_content_agent.db"),
        redis_url=getenv("REDIS_URL", "redis://localhost:6379/0"),
        log_level=getenv("LOG_LEVEL", "INFO"),
        database_echo=getenv("DATABASE_ECHO", "false").lower() in {"1", "true", "yes", "on"},
        anthropic_api_key=getenv("ANTHROPIC_API_KEY"),
        anthropic_model=getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest"),
        default_workspace_slug=getenv("DEFAULT_WORKSPACE_SLUG", "personal"),
        default_workspace_name=getenv("DEFAULT_WORKSPACE_NAME", "Personal Workspace"),
        default_user_external_id=getenv("DEFAULT_USER_EXTERNAL_ID", "demo-user"),
        default_user_email=getenv("DEFAULT_USER_EMAIL", "demo@example.com"),
        default_user_display_name=getenv("DEFAULT_USER_DISPLAY_NAME", "Demo User"),
        search_result_limit=int(getenv("SEARCH_RESULT_LIMIT", "10")),
        extraction_result_limit=int(getenv("EXTRACTION_RESULT_LIMIT", "10")),
        connector_clip_limit=int(getenv("CONNECTOR_CLIP_LIMIT", "6")),
        enable_mock_connectors=getenv("ENABLE_MOCK_CONNECTORS", "true").lower() == "true",
        enable_mock_extraction=getenv("ENABLE_MOCK_EXTRACTION", "true").lower() == "true",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return load_settings()
