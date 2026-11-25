"""Recent YouTube search signals used as optional discovery keywords.

The YouTube Data API does not expose a universal search-volume or trending-keyword
endpoint. This service extracts terms from recent, high-view related video titles;
these are discovery signals, not measured trends or SEO guarantees.
"""

import re
from datetime import datetime, timedelta, timezone

import requests


class YouTubeKeywordDiscovery:
    def __init__(
        self,
        api_key: str,
        region_code: str = "US",
        timeout: int = 30,
        session: requests.Session | None = None,
    ) -> None:
        self.api_key = api_key
        self.region_code = region_code
        self.timeout = timeout
        self.session = session or requests.Session()

    def discover(self, genre: str, limit: int = 20) -> list[str]:
        if not self.api_key:
            return []
        if not 1 <= limit <= 50:
            raise ValueError("Keyword discovery limit must be between 1 and 50.")
        response = self.session.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part": "snippet",
                "type": "video",
                "q": genre,
                "order": "viewCount",
                "publishedAfter": (datetime.now(timezone.utc) - timedelta(days=7))
                .isoformat(timespec="seconds")
                .replace("+00:00", "Z"),
                "regionCode": self.region_code,
                "maxResults": limit,
                "key": self.api_key,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        titles = [
            item.get("snippet", {}).get("title", "")
            for item in response.json().get("items", [])
        ]
        return _extract_terms(titles, genre, limit=20)


def _extract_terms(titles: list[str], genre: str, limit: int) -> list[str]:
    stop_words = {
        "the",
        "and",
        "for",
        "with",
        "from",
        "that",
        "this",
        "you",
        "your",
        "official",
        "video",
        "music",
        "hour",
        "hours",
        "min",
        "mins",
        "hd",
        "4k",
        "new",
        "best",
        "of",
        "to",
        "in",
        "on",
        "a",
        "an",
        "by",
    }
    genre_words = set(re.findall(r"[a-z0-9]+", genre.casefold()))
    counts: dict[str, int] = {}
    for title in titles:
        words = re.findall(r"[a-z0-9]+", title.casefold())
        for word in words:
            if len(word) >= 3 and word not in stop_words and word not in genre_words:
                counts[word] = counts.get(word, 0) + 1
    return [
        word
        for word, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[
            :limit
        ]
    ]
