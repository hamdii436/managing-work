"""Offline tests for AI music and YouTube automation contracts."""

from datetime import date, datetime, timezone

import pytest

from automation.config import Settings
from automation.models import AnalyticsMetrics, ContentMetadata
from automation.pipeline import AutomationPipeline
from automation.providers.gemini import GeminiClient
from automation.providers.music import HttpMusicProvider
from automation.providers.youtube import YouTubeClient, _youtube_tags
from automation.services.keywords import _extract_terms
from automation.services.title_experiments import TitleExperimentService


def valid_metadata():
    return {
        "music_prompt": "Original slow ambient instrumental with soft piano.",
        "title": "Quiet Dawn",
        "alternate_title": "Soft Piano at Sunrise",
        "description": "Original ambient instrumental.",
        "tags": ["ambient", "piano"],
        "thumbnail_prompt": "A calm sunrise over a lake, no text.",
        "seo_keywords": ["relaxing piano", "ambient"],
    }


def test_metadata_validation_rejects_duplicate_titles_and_excess_length():
    metadata = valid_metadata()
    metadata["alternate_title"] = metadata["title"]
    with pytest.raises(ValueError, match="different"):
        ContentMetadata.from_mapping(metadata)

    metadata = valid_metadata()
    metadata["title"] = "x" * 101
    with pytest.raises(ValueError, match="100 characters"):
        ContentMetadata.from_mapping(metadata)


def test_gemini_metadata_request_is_json_and_validated():
    class Response(FakeResponse):
        pass

    class Session:
        def post(self, url, **kwargs):
            assert "gemini-2.5-pro:generateContent" in url
            assert (
                kwargs["json"]["generationConfig"]["responseMimeType"]
                == "application/json"
            )
            body = {
                "candidates": [
                    {"content": {"parts": [{"text": json.dumps(valid_metadata())}]}}
                ]
            }
            return Response(body)

    import json

    client = GeminiClient("test-key", session=Session())
    generated = client.generate_metadata("ambient", ["deep focus", "sleep"])
    assert generated.title == "Quiet Dawn"
    assert generated.seo_keywords == ["relaxing piano", "ambient"]


def test_youtube_tags_are_deduplicated_and_within_limit():
    content = ContentMetadata.from_mapping(valid_metadata())
    tags = _youtube_tags(content)
    assert tags == ["ambient", "piano", "relaxing piano"]
    assert sum(map(len, tags)) + len(tags) - 1 <= 500


def test_keyword_extraction_uses_recurring_recent_title_terms():
    terms = _extract_terms(
        [
            "Ambient music for deep focus and study",
            "Deep focus ambient music for work",
            "Soft piano for sleep",
        ],
        "ambient",
        limit=10,
    )
    assert terms[:2] == ["deep", "focus"]
    assert "ambient" not in terms


class FakeResponse:
    def __init__(self, body=None, headers=None, content=b"audio"):
        self.body = body or {}
        self.headers = headers or {}
        self.content = content

    def raise_for_status(self):
        return None

    def json(self):
        return self.body

    def iter_content(self, chunk_size):
        yield self.content


class FakeMusicSession:
    def __init__(self):
        self.headers = {}
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append(("post", url, kwargs))
        return FakeResponse({"id": "job-1"})

    def get(self, url, **kwargs):
        self.calls.append(("get", url, kwargs))
        if url.endswith("/job-1"):
            return FakeResponse(
                {"status": "completed", "audio_url": "https://audio.test/a.mp3"}
            )
        return FakeResponse(content=b"valid audio")


def test_music_provider_submits_polls_and_downloads_audio(tmp_path):
    session = FakeMusicSession()
    provider = HttpMusicProvider(
        "https://music.test", "token", timeout_seconds=2, session=session
    )
    output = provider.generate("ambient instrumental", tmp_path / "track.mp3")
    assert output.read_bytes() == b"valid audio"
    assert [call[0] for call in session.calls] == ["post", "get", "get"]
    assert session.headers["Authorization"] == "Bearer token"


def test_music_provider_rejects_insecure_base_url():
    with pytest.raises(ValueError, match="HTTPS"):
        HttpMusicProvider("http://music.test")


class FakeYouTube:
    def __init__(self, metrics):
        self.metrics = metrics
        self.titles = []
        self.ranges = []

    def get_analytics(self, video_id, start_date, end_date):
        self.ranges.append((video_id, start_date, end_date))
        return self.metrics.pop(0)

    def set_title(self, video_id, title):
        self.titles.append((video_id, title))


def test_title_experiment_rotates_titles_and_records_winner(tmp_path):
    youtube = FakeYouTube(
        [
            AnalyticsMetrics(
                views=120,
                estimated_minutes_watched=900,
                average_view_duration=7.5,
                likes=10,
            ),
            AnalyticsMetrics(
                views=180,
                estimated_minutes_watched=1500,
                average_view_duration=8.3,
                likes=16,
            ),
        ]
    )
    service = TitleExperimentService(
        tmp_path / "tests.sqlite3", youtube, period_hours=24, minimum_views=100
    )
    start = datetime(2026, 11, 1, tzinfo=timezone.utc)
    service.start("video-id", "Title A", "Title B", start)

    assert service.advance_due(datetime(2026, 11, 1, 23, tzinfo=timezone.utc)) == 0
    assert service.advance_due(datetime(2026, 11, 2, tzinfo=timezone.utc)) == 1
    assert youtube.titles == [("video-id", "Title B")]
    assert service.advance_due(datetime(2026, 11, 2, 23, tzinfo=timezone.utc)) == 0
    assert service.advance_due(datetime(2026, 11, 3, tzinfo=timezone.utc)) == 1
    assert youtube.titles[-1] == ("video-id", "Title B")

    import sqlite3

    with sqlite3.connect(tmp_path / "tests.sqlite3") as connection:
        row = connection.execute(
            "SELECT status, winner, sufficient_data FROM title_experiments WHERE video_id=?",
            ("video-id",),
        ).fetchone()
    assert row == ("complete", "b", 1)


def test_title_experiment_marks_low_views_inconclusive(tmp_path):
    youtube = FakeYouTube(
        [
            AnalyticsMetrics(
                views=4,
                estimated_minutes_watched=20,
                average_view_duration=5,
                likes=0,
            ),
            AnalyticsMetrics(
                views=5,
                estimated_minutes_watched=30,
                average_view_duration=6,
                likes=1,
            ),
        ]
    )
    service = TitleExperimentService(
        tmp_path / "tests.sqlite3", youtube, period_hours=24, minimum_views=100
    )
    start = datetime(2026, 11, 1, tzinfo=timezone.utc)
    service.start("video-id", "Title A", "Title B", start)
    service.advance_due(datetime(2026, 11, 2, tzinfo=timezone.utc))
    service.advance_due(datetime(2026, 11, 3, tzinfo=timezone.utc))
    assert youtube.titles == [("video-id", "Title B"), ("video-id", "Title A")]
    import sqlite3

    with sqlite3.connect(tmp_path / "tests.sqlite3") as connection:
        row = connection.execute(
            "SELECT winner, sufficient_data FROM title_experiments"
        ).fetchone()
    assert row == (None, 0)


def test_title_experiment_requires_full_day_analytics_period(tmp_path):
    with pytest.raises(ValueError, match="multiple of 24"):
        TitleExperimentService(
            tmp_path / "tests.sqlite3", FakeYouTube([]), period_hours=12
        )


def test_settings_limit_is_capped_at_ten(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "not-a-real-key")
    monkeypatch.setenv("MUSIC_GENRE", "ambient")
    monkeypatch.setenv("DAILY_CONTENT_LIMIT", "11")
    settings = Settings.from_env()
    with pytest.raises(ValueError, match="between 1 and 10"):
        settings.validate()


def test_upload_reservations_enforce_daily_limit_atomically(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("MUSIC_GENRE", "ambient")
    monkeypatch.setenv("DAILY_CONTENT_LIMIT", "2")
    monkeypatch.setenv("AUTOMATION_DATABASE_PATH", str(tmp_path / "automation.sqlite3"))
    settings = Settings.from_env()
    pipeline = AutomationPipeline.__new__(AutomationPipeline)
    pipeline.settings = settings
    pipeline._initialize_database()

    assert pipeline._reserve_run("slot-1") is True
    assert pipeline._reserve_run("slot-1") is False
    pipeline._mark_complete("slot-1")
    assert pipeline._reserve_run("slot-2") is True
    pipeline._mark_uploading("slot-2")
    pipeline._mark_uploaded("slot-2", "video-2")
    with pytest.raises(RuntimeError, match="Daily content cap"):
        pipeline._reserve_run("slot-3")


def test_youtube_client_requires_user_oauth_credentials():
    with pytest.raises(ValueError, match="user OAuth"):
        YouTubeClient("", "", "")


def test_youtube_title_update_only_sends_writable_snippet_fields():
    class Session:
        def __init__(self):
            self.updated = None

        def post(self, url, **kwargs):
            return FakeResponse({"access_token": "access", "expires_in": 3600})

        def get(self, url, **kwargs):
            return FakeResponse(
                {
                    "items": [
                        {
                            "snippet": {
                                "title": "Old",
                                "description": "Description",
                                "tags": ["tag"],
                                "categoryId": "10",
                                "channelId": "read-only",
                                "publishedAt": "read-only",
                            }
                        }
                    ]
                }
            )

        def put(self, url, **kwargs):
            self.updated = kwargs["json"]
            return FakeResponse({})

    session = Session()
    youtube = YouTubeClient("client", "secret", "refresh")
    youtube.session = session
    youtube.set_title("video-id", "New")
    assert session.updated["snippet"] == {
        "title": "New",
        "description": "Description",
        "tags": ["tag"],
        "categoryId": "10",
    }


def test_youtube_analytics_uses_supported_metrics():
    class Session:
        def post(self, url, **kwargs):
            return FakeResponse({"access_token": "access", "expires_in": 3600})

        def get(self, url, **kwargs):
            assert kwargs["params"]["metrics"] == (
                "views,estimatedMinutesWatched,averageViewDuration,likes"
            )
            return FakeResponse({"rows": [[75, 320.5, 4.25, 8]]})

    youtube = YouTubeClient("client", "secret", "refresh")
    youtube.session = Session()
    metrics = youtube.get_analytics("video-id", date(2026, 11, 1), date(2026, 11, 1))
    assert metrics == AnalyticsMetrics(75, 320.5, 4.25, 8)


def test_playlist_addition_is_idempotent_when_video_is_already_present():
    class Session:
        def __init__(self):
            self.inserted = False

        def post(self, url, **kwargs):
            return FakeResponse({"access_token": "access", "expires_in": 3600})

        def get(self, url, **kwargs):
            return FakeResponse({"items": [{"id": "playlist-entry"}]})

    youtube = YouTubeClient("client", "secret", "refresh")
    session = Session()
    youtube.session = session
    youtube.add_to_playlist("video-id", "playlist-id")
    assert session.inserted is False
