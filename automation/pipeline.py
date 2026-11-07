"""Orchestrates keyword research, metadata, audio, video, and optional publishing."""

import json
import re
import sqlite3
from datetime import datetime, timezone

from automation.config import Settings
from automation.models import ContentMetadata
from automation.providers.gemini import GeminiClient
from automation.providers.music import HttpMusicProvider
from automation.providers.youtube import YouTubeClient
from automation.services.keywords import YouTubeKeywordDiscovery
from automation.services.title_experiments import TitleExperimentService
from automation.services.video import VideoRenderer


class AutomationPipeline:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        settings.validate()
        settings.output_dir.mkdir(parents=True, exist_ok=True)
        settings.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.gemini = GeminiClient(
            settings.gemini_api_key, settings.gemini_model, settings.request_timeout
        )
        self.keyword_discovery = YouTubeKeywordDiscovery(
            settings.youtube_api_key, settings.region_code, settings.request_timeout
        )
        self.music = HttpMusicProvider(
            settings.music_api_url,
            settings.music_api_token,
            poll_interval_seconds=settings.music_poll_interval,
            timeout_seconds=settings.music_job_timeout,
        )
        self.renderer = VideoRenderer(settings.ffmpeg_path)
        self._initialize_database()

    def run_once(self) -> dict[str, str | bool]:
        """Create one item; upload only when explicitly enabled in environment."""
        slot = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H")
        run = self._get_run(slot)
        if run and run["status"] == "complete":
            return {"status": "skipped", "reason": "hourly slot already completed"}

        if run and run["status"] == "uploading" and not run["video_id"]:
            raise RuntimeError(
                f"Upload for slot {slot} may have reached YouTube before interruption. "
                "Check the channel and reconcile this slot before retrying."
            )

        if run and run["status"] == "generating" and not run["video_id"]:
            raise RuntimeError(
                f"Generation for slot {slot} was interrupted. Inspect local artifacts "
                "before retrying."
            )

        if run and run["video_id"]:
            if not self.settings.publish_enabled:
                raise RuntimeError(
                    "This hourly slot has an uploaded video with unfinished post-upload "
                    "steps; enable publishing to resume it safely."
                )
            content = ContentMetadata.from_mapping(json.loads(run["metadata_json"]))
            return self._finish_publishing(slot, content, run["video_id"])

        if self.settings.publish_enabled:
            self.settings.validate(require_youtube=True)

        image_path = self.settings.content_image
        if image_path is None:
            raise ValueError(
                "CONTENT_IMAGE_PATH must point to an image used to render the video."
            )
        if not image_path.is_file():
            raise FileNotFoundError(f"Video image does not exist: {image_path}")

        if not self._reserve_run(slot):
            run = self._get_run(slot)
            if run and run["status"] == "complete":
                return {"status": "skipped", "reason": "hourly slot already completed"}
            raise RuntimeError(
                f"Hourly slot {slot} is already in progress; inspect its SQLite state "
                "before retrying."
            )

        try:
            keywords = self.keyword_discovery.discover(self.settings.genre)
            content = self.gemini.generate_metadata(self.settings.genre, keywords)
            slug = _slug(content.title)
            audio_path = self.music.generate(
                content.music_prompt, self.settings.output_dir / f"{slot}-{slug}.mp3"
            )
            video_path = self.renderer.render(
                audio_path,
                image_path,
                self.settings.output_dir / f"{slot}-{slug}.mp4",
            )
            self._save_metadata(slot, content.as_dict())
        except Exception:
            self._mark_failed(slot)
            raise

        if self.settings.publish_enabled:
            self._mark_uploading(slot)
            youtube = self._youtube()
            video_id = youtube.upload_video(
                video_path, content, self.settings.youtube_privacy_status
            )
            self._mark_uploaded(slot, video_id)
            return self._finish_publishing(slot, content, video_id)

        self._mark_complete(slot)
        return {
            "status": "rendered_not_published",
            "video_id": "",
            "video_path": str(video_path),
        }

    def _finish_publishing(self, slot, content, video_id):
        run = self._get_run(slot)
        youtube = self._youtube()
        if self.settings.thumbnail_image and not run["thumbnail_done"]:
            youtube.upload_thumbnail(video_id, self.settings.thumbnail_image)
            self._mark_step(slot, "thumbnail_done")
        if self.settings.youtube_playlist_id and not run["playlist_done"]:
            youtube.add_to_playlist(video_id, self.settings.youtube_playlist_id)
            self._mark_step(slot, "playlist_done")
        if not run["experiment_started"]:
            TitleExperimentService(
                self.settings.database_path,
                youtube,
                self.settings.title_test_hours,
                self.settings.minimum_views,
            ).start(video_id, content.title, content.alternate_title)
            self._mark_step(slot, "experiment_started")
        with sqlite3.connect(self.settings.database_path) as connection:
            connection.execute(
                "UPDATE completed_runs SET status='complete' WHERE slot=?", (slot,)
            )
        return {"status": "published", "video_id": video_id}

    def process_title_experiments(self) -> int:
        if not self.settings.publish_enabled:
            return 0
        self.settings.validate(require_youtube=True)
        return TitleExperimentService(
            self.settings.database_path,
            self._youtube(),
            self.settings.title_test_hours,
            self.settings.minimum_views,
        ).advance_due()

    def _youtube(self) -> YouTubeClient:
        return YouTubeClient(
            self.settings.youtube_client_id,
            self.settings.youtube_client_secret,
            self.settings.youtube_refresh_token,
            self.settings.request_timeout,
        )

    def _initialize_database(self) -> None:
        with sqlite3.connect(self.settings.database_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS completed_runs (
                    slot TEXT PRIMARY KEY,
                    run_date TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    video_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    thumbnail_done INTEGER NOT NULL DEFAULT 0,
                    playlist_done INTEGER NOT NULL DEFAULT 0,
                    experiment_started INTEGER NOT NULL DEFAULT 0
                )
                """
            )

    def _get_run(self, slot: str):
        with sqlite3.connect(self.settings.database_path) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                "SELECT * FROM completed_runs WHERE slot=?", (slot,)
            ).fetchone()
            return dict(row) if row else None

    def _reserve_run(self, slot: str) -> bool:
        run_date = datetime.now(timezone.utc).date().isoformat()
        with sqlite3.connect(self.settings.database_path) as connection:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                "SELECT status FROM completed_runs WHERE slot=?", (slot,)
            ).fetchone()
            if existing and existing[0] != "failed":
                return False
            count = connection.execute(
                """
                SELECT COUNT(*) FROM completed_runs
                WHERE run_date=? AND status IN ('generating', 'uploading', 'uploaded', 'complete')
                """,
                (run_date,),
            ).fetchone()[0]
            if count >= self.settings.daily_limit:
                raise RuntimeError(
                    f"Daily content cap ({self.settings.daily_limit}) has been reached."
                )
            if existing:
                connection.execute(
                    """
                    UPDATE completed_runs
                    SET run_date=?, metadata_json='', video_id='', status='generating',
                        thumbnail_done=0, playlist_done=0, experiment_started=0
                    WHERE slot=?
                    """,
                    (run_date, slot),
                )
            else:
                connection.execute(
                    """
                    INSERT INTO completed_runs
                    (slot, run_date, metadata_json, video_id, status)
                    VALUES (?, ?, '', '', 'generating')
                    """,
                    (slot, run_date),
                )
        return True

    def _save_metadata(self, slot: str, metadata: dict) -> None:
        with sqlite3.connect(self.settings.database_path) as connection:
            connection.execute(
                "UPDATE completed_runs SET metadata_json=? WHERE slot=?",
                (json.dumps(metadata, ensure_ascii=False), slot),
            )

    def _mark_failed(self, slot: str) -> None:
        with sqlite3.connect(self.settings.database_path) as connection:
            connection.execute(
                "UPDATE completed_runs SET status='failed' WHERE slot=? AND status='generating'",
                (slot,),
            )

    def _mark_uploading(self, slot: str) -> None:
        with sqlite3.connect(self.settings.database_path) as connection:
            connection.execute(
                "UPDATE completed_runs SET status='uploading' WHERE slot=?", (slot,)
            )

    def _mark_uploaded(self, slot: str, video_id: str) -> None:
        with sqlite3.connect(self.settings.database_path) as connection:
            connection.execute(
                "UPDATE completed_runs SET video_id=?, status='uploaded' WHERE slot=?",
                (video_id, slot),
            )

    def _mark_complete(self, slot: str) -> None:
        with sqlite3.connect(self.settings.database_path) as connection:
            connection.execute(
                "UPDATE completed_runs SET status='complete' WHERE slot=?", (slot,)
            )

    def _mark_step(self, slot: str, column: str) -> None:
        if column not in {"thumbnail_done", "playlist_done", "experiment_started"}:
            raise ValueError(f"Unknown upload step: {column}")
        with sqlite3.connect(self.settings.database_path) as connection:
            connection.execute(
                f"UPDATE completed_runs SET {column}=1 WHERE slot=?", (slot,)
            )


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-")
    return slug[:60] or "music"
