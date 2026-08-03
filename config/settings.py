"""Settings management using Pydantic."""

from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.enums import LogLevel, Theme


class Settings(BaseSettings):
    """Application settings from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="Google Maps Business Automation")
    app_version: str = Field(default="1.0.0")
    app_debug: bool = Field(default=False)
    app_log_level: LogLevel = Field(default=LogLevel.INFO)
    app_theme: Theme = Field(default=Theme.DARK)

    # Database
    database_path: str = Field(default="./data/database.db")
    database_backup_enabled: bool = Field(default=True)
    database_backup_path: str = Field(default="./data/backups")

    # Export
    export_path: str = Field(default="./exports")
    export_chunk_size: int = Field(default=1000)

    # Scraper
    scraper_timeout: int = Field(default=30)
    scraper_retry_attempts: int = Field(default=3)
    scraper_retry_delay: int = Field(default=2)
    scraper_rate_limit_delay: int = Field(default=2)
    scraper_user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    scraper_headless: bool = Field(default=True)
    scraper_browser: str = Field(default="chromium")

    # Search
    search_max_results_per_category: int = Field(default=500)
    search_max_concurrent_threads: int = Field(default=3)
    search_timeout: int = Field(default=120)
    search_cache_enabled: bool = Field(default=True)
    search_cache_ttl: int = Field(default=3600)

    # Plugin
    plugin_enabled: bool = Field(default=True)
    plugin_path: str = Field(default="./plugins")
    plugin_auto_load: bool = Field(default=True)

    # Logging
    log_level: LogLevel = Field(default=LogLevel.INFO)
    log_file_path: str = Field(default="./logs")
    log_max_size: int = Field(default=10485760)
    log_backup_count: int = Field(default=5)
    log_format: str = Field(default="json")

    # UI
    ui_window_width: int = Field(default=1200)
    ui_window_height: int = Field(default=800)
    ui_auto_save_window_state: bool = Field(default=True)
    ui_animation_enabled: bool = Field(default=True)

    # API Rate Limiting
    api_rate_limit_enabled: bool = Field(default=True)
    api_rate_limit_requests: int = Field(default=100)
    api_rate_limit_period: int = Field(default=60)

    # Auto-update
    auto_update_enabled: bool = Field(default=False)
    auto_update_check_interval: int = Field(default=86400)
    update_url: Optional[str] = Field(default=None)

    # Performance
    cache_enabled: bool = Field(default=True)
    cache_size: int = Field(default=100)
    results_pagination_size: int = Field(default=50)

    # Feature Flags
    feature_advanced_filters: bool = Field(default=True)
    feature_batch_search: bool = Field(default=True)
    feature_search_history: bool = Field(default=True)
    feature_duplicate_detection: bool = Field(default=True)
    feature_scheduled_searches: bool = Field(default=False)

    @field_validator("database_path", "export_path", "log_file_path", "plugin_path", mode="after")
    @classmethod
    def create_directories(cls, v: str) -> str:
        """Create directories if they don't exist."""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return v

    @field_validator("scraper_timeout", "scraper_retry_attempts", "search_timeout", mode="after")
    @classmethod
    def validate_positive_int(cls, v: int) -> int:
        """Ensure integer values are positive."""
        if v <= 0:
            raise ValueError("Value must be positive")
        return v

    class Config:
        """Pydantic config."""

        protected_namespaces = ()


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment."""
    global _settings
    _settings = Settings()
    return _settings
