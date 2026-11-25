"""Validated metadata contracts shared by automation services."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ContentMetadata:
    music_prompt: str
    title: str
    alternate_title: str
    description: str
    tags: list[str]
    thumbnail_prompt: str
    seo_keywords: list[str]

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "ContentMetadata":
        fields = (
            "music_prompt",
            "title",
            "alternate_title",
            "description",
            "tags",
            "thumbnail_prompt",
            "seo_keywords",
        )
        missing = [field for field in fields if field not in value]
        if missing:
            raise ValueError(f"Gemini response is missing: {', '.join(missing)}")
        result = cls(
            music_prompt=_text(value["music_prompt"], "music_prompt"),
            title=_text(value["title"], "title"),
            alternate_title=_text(value["alternate_title"], "alternate_title"),
            description=_text(value["description"], "description"),
            tags=_string_list(value["tags"], "tags"),
            thumbnail_prompt=_text(value["thumbnail_prompt"], "thumbnail_prompt"),
            seo_keywords=_string_list(value["seo_keywords"], "seo_keywords"),
        )
        if len(result.title) > 100 or len(result.alternate_title) > 100:
            raise ValueError("YouTube titles must be 100 characters or fewer.")
        if result.title == result.alternate_title:
            raise ValueError("The A/B title variants must be different.")
        if len(result.description) > 5000:
            raise ValueError("YouTube descriptions must be at most 5,000 characters.")
        if sum(map(len, result.tags)) + max(0, len(result.tags) - 1) > 500:
            raise ValueError("Combined YouTube tags must be at most 500 characters.")
        return result

    def as_dict(self) -> dict[str, Any]:
        return {
            "music_prompt": self.music_prompt,
            "title": self.title,
            "alternate_title": self.alternate_title,
            "description": self.description,
            "tags": self.tags,
            "thumbnail_prompt": self.thumbnail_prompt,
            "seo_keywords": self.seo_keywords,
        }


@dataclass(frozen=True)
class AnalyticsMetrics:
    views: int
    estimated_minutes_watched: float
    average_view_duration: float
    likes: int


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text.")
    return value.strip()


def _string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise ValueError(f"{field} must be a list of non-empty strings.")
    return list(dict.fromkeys(item.strip() for item in value))
