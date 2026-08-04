"""Settings management using Pydantic."""

from pathlib import Path
from typing import Optional
import logging

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.enums import LogLevel, Theme

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings from environment variables with validation."""

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
    database_pool_size: int = Field(default=10, ge=1, le=100)
    database_pool_timeout: int = Field(default=30, ge=5, le=300)

    # Export
    export_path: str = Field(default="./exports")
    export_chunk_size: int = Field(default=1000, ge=100, le=10000)

    # Scraper
    scraper_timeout: int = Field(default=30, ge=5, le=300)
    scraper_retry_attempts: int = Field(default=3, ge=1, le=10)
    scraper_retry_delay: int = Field(default=2, ge=1, le=30)
    scraper_rate_limit_delay: int = Field(default=2, ge=1, le=60)
    scraper_user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    scraper_headless: bool = Field(default=True)
    scraper_browser: str = Field(default="chromium")

    # Search
    search_max_results_per_category: int = Field(default=500, ge=10, le=5000)
    search_max_concurrent_threads: int = Field(default=3, ge=1, le=20)
    search_timeout: int = Field(default=120, ge=30, le=600)
    search_cache_enabled: bool = Field(default=True)
    search_cache_ttl: int = Field(default=3600, ge=60, le=86400)

    # Plugin
    plugin_enabled: bool = Field(default=True)
    plugin_path: str = Field(default="./plugins")
    plugin_auto_load: bool = Field(default=True)

    # Logging
    log_level: LogLevel = Field(default=LogLevel.INFO)
    log_file_path: str = Field(default="./logs")
    log_max_size: int = Field(default=10485760, ge=1000000, le=1000000000)
    log_backup_count: int = Field(default=5, ge=1, le=100)
    log_format: str = Field(default="text")  # text or json
    log_console_output: bool = Field(default=True)

    # UI
    ui_window_width: int = Field(default=1200, ge=800, le=4000)
    ui_window_height: int = Field(default=800, ge=600, le=3000)
    ui_auto_save_window_state: bool = Field(default=True)
    ui_animation_enabled: bool = Field(default=True)
    ui_animation_duration: int = Field(default=300, ge=0, le=1000)

    # API Rate Limiting
    api_rate_limit_enabled: bool = Field(default=True)
    api_rate_limit_requests: int = Field(default=100, ge=1, le=10000)
    api_rate_limit_period: int = Field(default=60, ge=1, le=3600)

    # Auto-update
    auto_update_enabled: bool = Field(default=False)
    auto_update_check_interval: int = Field(default=86400, ge=3600, le=2592000)
    update_url: Optional[str] = Field(default=None)

    # Performance
    cache_enabled: bool = Field(default=True)
    cache_size: int = Field(default=100, ge=10, le=1000)
    results_pagination_size: int = Field(default=50, ge=10, le=500)

    # Feature Flags
    feature_advanced_filters: bool = Field(default=True)
    feature_batch_search: bool = Field(default=True)
    feature_search_history: bool = Field(default=True)
    feature_duplicate_detection: bool = Field(default=True)
    feature_scheduled_searches: bool = Field(default=False)
    feature_resume_interrupted: bool = Field(default=True)

    @field_validator("database_path", "export_path", "log_file_path", "plugin_path", mode="before")
    @classmethod
    def expand_paths(cls, v: str) -> str:
        """Expand user paths (~)."""
        if isinstance(v, str):
            return str(Path(v).expanduser())
        return v

    @field_validator("database_path", "export_path", "log_file_path", "plugin_path", mode="after")
    @classmethod
    def create_directories(cls, v: str) -> str:
        """Create directories if they don't exist."""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return v

    @field_validator("log_max_size", "database_pool_size", "cache_size", mode="after")
    @classmethod
    def validate_positive_int(cls, v: int) -> int:
        """Ensure integer values are positive."""
        if v <= 0:
            raise ValueError("Value must be positive")
        return v

    def to_dict(self) -> dict:
        """Export settings as dictionary."""
        return self.model_dump()

    def to_env_file(self, path: Path) -> None:
        """Export settings to .env file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            for key, value in self.model_dump().items():
                f.write(f"{key.upper()}={value}\n")
        logger.info(f"Settings exported to {path}")

    class Config:
        """Pydantic config."""

        protected_namespaces = ()


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings instance (singleton)."""
    global _settings
    if _settings is None:
        _settings = Settings()
        logger.info(f"Settings loaded from {_settings.model_config.get('env_file', '.env')}")
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment."""
    global _settings
    _settings = Settings()
    logger.info("Settings reloaded")
    return _settings


def reset_settings() -> None:
    """Reset settings singleton."""
    global _settings
    _settings = None


def validate_settings() -> tuple[bool, list[str]]:
    """Validate current settings."""
    try:
        settings = get_settings()
        errors = []
        
        # Check database connectivity
        db_path = Path(settings.database_path)
        if not db_path.parent.exists():
            errors.append(f"Database directory doesn't exist: {db_path.parent}")
        
        # Check export directory
        export_path = Path(settings.export_path)
        if not export_path.exists():
            export_path.mkdir(parents=True, exist_ok=True)
        
        # Check log directory
        log_path = Path(settings.log_file_path)
        if not log_path.exists():
            log_path.mkdir(parents=True, exist_ok=True)
        
        return len(errors) == 0, errors
    except Exception as e:
        return False, [str(e)]

