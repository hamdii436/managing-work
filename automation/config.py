"""Environment-backed configuration for the automation prototype."""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str
    gemini_model: str
    genre: str
    region_code: str
    youtube_api_key: str
    daily_limit: int
    music_api_url: str
    music_api_token: str
    music_poll_interval: int
    music_job_timeout: int
    youtube_client_id: str
    youtube_client_secret: str
    youtube_refresh_token: str
    youtube_playlist_id: str
    youtube_privacy_status: str
    publish_enabled: bool
    content_image: Path | None
    thumbnail_image: Path | None
    output_dir: Path
    database_path: Path
    ffmpeg_path: str
    title_test_hours: int
    minimum_views: int
    request_timeout: int
    scheduler_enabled: bool

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-pro"),
            genre=os.getenv("MUSIC_GENRE", ""),
            region_code=os.getenv("YOUTUBE_REGION_CODE", "US"),
            youtube_api_key=os.getenv("YOUTUBE_API_KEY", ""),
            daily_limit=_int_env("DAILY_CONTENT_LIMIT", 8),
            music_api_url=os.getenv("MUSIC_API_URL", "").rstrip("/"),
            music_api_token=os.getenv("MUSIC_API_TOKEN", ""),
            music_poll_interval=_int_env("MUSIC_POLL_INTERVAL_SECONDS", 10),
            music_job_timeout=_int_env("MUSIC_JOB_TIMEOUT_SECONDS", 1800),
            youtube_client_id=os.getenv("YOUTUBE_CLIENT_ID", ""),
            youtube_client_secret=os.getenv("YOUTUBE_CLIENT_SECRET", ""),
            youtube_refresh_token=os.getenv("YOUTUBE_REFRESH_TOKEN", ""),
            youtube_playlist_id=os.getenv("YOUTUBE_PLAYLIST_ID", ""),
            youtube_privacy_status=os.getenv("YOUTUBE_PRIVACY_STATUS", "private"),
            publish_enabled=_bool_env("PUBLISH_ENABLED", False),
            content_image=_optional_path("CONTENT_IMAGE_PATH"),
            thumbnail_image=_optional_path("THUMBNAIL_IMAGE_PATH"),
            output_dir=Path(os.getenv("AUTOMATION_OUTPUT_DIR", "data/ai_music")),
            database_path=Path(
                os.getenv(
                    "AUTOMATION_DATABASE_PATH", "data/ai_music/automation.sqlite3"
                )
            ),
            ffmpeg_path=os.getenv("FFMPEG_PATH", "ffmpeg"),
            title_test_hours=_int_env("TITLE_TEST_HOURS", 24),
            minimum_views=_int_env("TITLE_TEST_MIN_VIEWS", 100),
            request_timeout=_int_env("API_TIMEOUT_SECONDS", 60),
            scheduler_enabled=_bool_env("SCHEDULER_ENABLED", False),
        )

    def validate(self, require_youtube: bool = False) -> None:
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required.")
        if not self.genre.strip():
            raise ValueError("MUSIC_GENRE is required (for example: ambient).")
        if not 1 <= self.daily_limit <= 10:
            raise ValueError("DAILY_CONTENT_LIMIT must be between 1 and 10.")
        if self.youtube_privacy_status not in {"private", "unlisted", "public"}:
            raise ValueError(
                "YOUTUBE_PRIVACY_STATUS must be private, unlisted, or public."
            )
        if self.title_test_hours < 24 or self.title_test_hours % 24:
            raise ValueError("TITLE_TEST_HOURS must be a positive multiple of 24.")
        if self.minimum_views <= 0:
            raise ValueError("TITLE_TEST_MIN_VIEWS must be positive.")
        if require_youtube:
            missing = [
                name
                for name, value in (
                    ("YOUTUBE_CLIENT_ID", self.youtube_client_id),
                    ("YOUTUBE_CLIENT_SECRET", self.youtube_client_secret),
                    ("YOUTUBE_REFRESH_TOKEN", self.youtube_refresh_token),
                )
                if not value
            ]
            if missing:
                raise ValueError("YouTube OAuth requires: " + ", ".join(missing))


def _int_env(name: str, default: int) -> int:
    value = int(os.getenv(name, str(default)))
    if value <= 0:
        raise ValueError(f"{name} must be a positive integer.")
    return value


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized not in {"true", "false", "1", "0", "yes", "no"}:
        raise ValueError(f"{name} must be true or false.")
    return normalized in {"true", "1", "yes"}


def _optional_path(name: str) -> Path | None:
    value = os.getenv(name, "").strip()
    return Path(value) if value else None
