"""YouTube Data API and Analytics API client using user OAuth refresh tokens."""

import time
from datetime import date
from pathlib import Path
from urllib.parse import urlencode

import requests

from automation.models import AnalyticsMetrics, ContentMetadata


class YouTubeClient:
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    DATA_API = "https://www.googleapis.com/youtube/v3"
    ANALYTICS_API = "https://youtubeanalytics.googleapis.com/v2/reports"
    UPLOAD_API = "https://www.googleapis.com/upload/youtube/v3/videos"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        timeout: int = 60,
    ) -> None:
        if not all((client_id, client_secret, refresh_token)):
            raise ValueError(
                "YouTube upload requires user OAuth client ID, secret, and refresh token."
            )
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.timeout = timeout
        self.session = requests.Session()
        self._access_token = ""
        self._expires_at = 0.0

    def upload_video(
        self,
        video_path: Path,
        content: ContentMetadata,
        privacy_status: str = "private",
    ) -> str:
        if not video_path.is_file():
            raise FileNotFoundError(f"Video does not exist: {video_path}")
        if privacy_status not in {"private", "unlisted", "public"}:
            raise ValueError("Invalid YouTube privacy status.")
        metadata = {
            "snippet": {
                "title": content.title,
                "description": content.description,
                "tags": _youtube_tags(content),
                "categoryId": "10",
            },
            "status": {"privacyStatus": privacy_status},
        }
        response = self.session.post(
            f"{self.UPLOAD_API}?{urlencode({'uploadType': 'resumable', 'part': 'snippet,status'})}",
            headers={
                **self._headers(),
                "Content-Type": "application/json; charset=UTF-8",
                "X-Upload-Content-Type": "video/mp4",
                "X-Upload-Content-Length": str(video_path.stat().st_size),
            },
            json=metadata,
            timeout=self.timeout,
        )
        response.raise_for_status()
        upload_url = response.headers.get("Location")
        if not upload_url:
            raise ValueError("YouTube did not return a resumable upload URL.")
        with video_path.open("rb") as media:
            uploaded = self.session.put(
                upload_url,
                headers={**self._headers(), "Content-Type": "video/mp4"},
                data=media,
                timeout=(self.timeout, 1800),
            )
        uploaded.raise_for_status()
        video_id = uploaded.json().get("id")
        if not isinstance(video_id, str) or not video_id:
            raise ValueError("YouTube upload response did not contain a video id.")
        return video_id

    def upload_thumbnail(self, video_id: str, image_path: Path) -> None:
        if not image_path.is_file():
            raise FileNotFoundError(f"Thumbnail does not exist: {image_path}")
        suffix = image_path.suffix.lower()
        if suffix not in {".png", ".jpg", ".jpeg"}:
            raise ValueError("YouTube thumbnails must be PNG or JPEG files.")
        if image_path.stat().st_size > 2 * 1024 * 1024:
            raise ValueError("YouTube thumbnail files must not exceed 2 MiB.")
        content_type = "image/png" if suffix == ".png" else "image/jpeg"
        with image_path.open("rb") as image:
            response = self.session.post(
                f"{self.DATA_API}/thumbnails/set",
                params={"videoId": video_id},
                headers={**self._headers(), "Content-Type": content_type},
                data=image,
                timeout=self.timeout,
            )
        response.raise_for_status()

    def add_to_playlist(self, video_id: str, playlist_id: str) -> None:
        existing = self.session.get(
            f"{self.DATA_API}/playlistItems",
            params={
                "part": "id",
                "playlistId": playlist_id,
                "videoId": video_id,
                "maxResults": 50,
            },
            headers=self._headers(),
            timeout=self.timeout,
        )
        existing.raise_for_status()
        if existing.json().get("items", []):
            return
        response = self.session.post(
            f"{self.DATA_API}/playlistItems",
            params={"part": "snippet"},
            headers=self._headers(),
            json={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {"kind": "youtube#video", "videoId": video_id},
                }
            },
            timeout=self.timeout,
        )
        response.raise_for_status()

    def set_title(self, video_id: str, title: str) -> None:
        current = self.session.get(
            f"{self.DATA_API}/videos",
            params={"part": "snippet", "id": video_id},
            headers=self._headers(),
            timeout=self.timeout,
        )
        current.raise_for_status()
        items = current.json().get("items", [])
        if not items:
            raise ValueError(f"YouTube video {video_id} was not found.")
        snippet = items[0]["snippet"]
        writable_snippet = {
            key: snippet[key]
            for key in ("description", "tags", "categoryId")
            if key in snippet
        }
        writable_snippet["title"] = title
        response = self.session.put(
            f"{self.DATA_API}/videos",
            params={"part": "snippet"},
            headers=self._headers(),
            json={"id": video_id, "snippet": writable_snippet},
            timeout=self.timeout,
        )
        response.raise_for_status()

    def get_analytics(
        self, video_id: str, start_date: date, end_date: date
    ) -> AnalyticsMetrics:
        response = self.session.get(
            self.ANALYTICS_API,
            params={
                "ids": "channel==MINE",
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat(),
                "metrics": "views,estimatedMinutesWatched,averageViewDuration,likes",
                "filters": f"video=={video_id}",
            },
            headers=self._headers(),
            timeout=self.timeout,
        )
        response.raise_for_status()
        rows = response.json().get("rows", [])
        if not rows:
            return AnalyticsMetrics(
                views=0,
                estimated_minutes_watched=0.0,
                average_view_duration=0.0,
                likes=0,
            )
        return AnalyticsMetrics(
            views=int(rows[0][0]),
            estimated_minutes_watched=float(rows[0][1]),
            average_view_duration=float(rows[0][2]),
            likes=int(rows[0][3]),
        )

    def _headers(self) -> dict[str, str]:
        if not self._access_token or time.time() >= self._expires_at - 60:
            response = self.session.post(
                self.TOKEN_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": self.refresh_token,
                    "grant_type": "refresh_token",
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
            self._access_token = payload["access_token"]
            self._expires_at = time.time() + int(payload.get("expires_in", 3600))
        return {"Authorization": f"Bearer {self._access_token}"}


def _youtube_tags(content: ContentMetadata) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    size = 0
    for candidate in content.tags + content.seo_keywords:
        tag = " ".join(candidate.split()).strip()
        extra = len(tag) + (1 if result else 0)
        if not tag or tag.casefold() in seen or len(result) >= 30 or size + extra > 500:
            continue
        result.append(tag)
        seen.add(tag.casefold())
        size += extra
    return result
