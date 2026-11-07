"""Sequential two-title experiments backed by YouTube Analytics observations."""

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from automation.models import AnalyticsMetrics


class TitleExperimentService:
    def __init__(
        self,
        database_path: Path,
        youtube,
        period_hours: int = 24,
        minimum_views: int = 100,
    ) -> None:
        if period_hours < 24 or period_hours % 24 or minimum_views <= 0:
            raise ValueError(
                "Experiment period must be a multiple of 24 hours and the view threshold positive."
            )
        self.database_path = database_path
        self.youtube = youtube
        self.period_hours = period_hours
        self.minimum_views = minimum_views
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS title_experiments (
                    video_id TEXT PRIMARY KEY,
                    title_a TEXT NOT NULL,
                    title_b TEXT NOT NULL,
                    active_variant TEXT NOT NULL,
                    period_started TEXT NOT NULL,
                    status TEXT NOT NULL,
                    winner TEXT,
                    sufficient_data INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS title_observations (
                    video_id TEXT NOT NULL,
                    variant TEXT NOT NULL,
                    title TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    views INTEGER NOT NULL,
                    estimated_minutes_watched REAL NOT NULL,
                    average_view_duration REAL NOT NULL,
                    likes INTEGER NOT NULL,
                    PRIMARY KEY (video_id, variant)
                );
                """
            )

    def start(
        self,
        video_id: str,
        title_a: str,
        title_b: str,
        now: datetime | None = None,
    ) -> None:
        if not title_a or not title_b or title_a == title_b:
            raise ValueError("The title experiment requires two different titles.")
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO title_experiments
                (video_id, title_a, title_b, active_variant, period_started, status)
                VALUES (?, ?, ?, 'a', ?, 'active')
                """,
                (video_id, title_a, title_b, _next_utc_midnight(_utc(now)).isoformat()),
            )

    def advance_due(self, now: datetime | None = None) -> int:
        current = _utc(now)
        with self._connect() as connection:
            experiments = connection.execute(
                "SELECT * FROM title_experiments WHERE status = 'active'"
            ).fetchall()
        advanced = 0
        for experiment in experiments:
            started = datetime.fromisoformat(experiment["period_started"])
            if current < started + timedelta(hours=self.period_hours):
                continue
            start_date = started.date()
            end_date = (current - timedelta(days=1)).date()
            if end_date < start_date:
                continue
            metrics = self.youtube.get_analytics(
                experiment["video_id"], start_date, end_date
            )
            self._record_period(experiment, started, current, metrics)
            advanced += 1
        return advanced

    def _record_period(
        self, experiment, started, now, metrics: AnalyticsMetrics
    ) -> None:
        video_id = experiment["video_id"]
        variant = experiment["active_variant"]
        title = experiment["title_a"] if variant == "a" else experiment["title_b"]
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO title_observations
                (video_id, variant, title, start_date, end_date, views,
                 estimated_minutes_watched, average_view_duration, likes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    video_id,
                    variant,
                    title,
                    started.date().isoformat(),
                    (now - timedelta(days=1)).date().isoformat(),
                    metrics.views,
                    metrics.estimated_minutes_watched,
                    metrics.average_view_duration,
                    metrics.likes,
                ),
            )
            if variant == "a":
                self.youtube.set_title(video_id, experiment["title_b"])
                connection.execute(
                    """
                    UPDATE title_experiments
                    SET active_variant='b', period_started=?
                    WHERE video_id=? AND status='active'
                    """,
                    (_utc_midnight(now).isoformat(), video_id),
                )
                return

            results = connection.execute(
                "SELECT variant, views FROM title_observations WHERE video_id=?",
                (video_id,),
            ).fetchall()
            sufficient = len(results) == 2 and all(
                row["views"] >= self.minimum_views for row in results
            )
            winner = None
            chosen_title = experiment["title_a"]
            if sufficient:
                winner = max(results, key=lambda row: row["views"])["variant"]
                chosen_title = (
                    experiment["title_a"] if winner == "a" else experiment["title_b"]
                )
            self.youtube.set_title(video_id, chosen_title)
            connection.execute(
                """
                UPDATE title_experiments
                SET status='complete', winner=?, sufficient_data=?
                WHERE video_id=?
                """,
                (winner, int(sufficient), video_id),
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection


def _utc(value: datetime | None) -> datetime:
    current = value or datetime.now(timezone.utc)
    if current.tzinfo is None:
        return current.replace(tzinfo=timezone.utc)
    return current.astimezone(timezone.utc)


def _next_utc_midnight(value: datetime) -> datetime:
    midnight = _utc_midnight(value)
    if value == midnight:
        return midnight
    return midnight + timedelta(days=1)


def _utc_midnight(value: datetime) -> datetime:
    return value.replace(hour=0, minute=0, second=0, microsecond=0)
