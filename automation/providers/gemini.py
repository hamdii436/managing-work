"""Gemini REST client for text-only creative metadata generation."""

import json

import requests

from automation.models import ContentMetadata


class GeminiClient:
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.5-pro",
        timeout: int = 60,
        session: requests.Session | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required.")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.session = session or requests.Session()

    def generate_metadata(
        self, genre: str, trend_keywords: list[str]
    ) -> ContentMetadata:
        keyword_context = (
            ", ".join(trend_keywords) if trend_keywords else "none available"
        )
        prompt = (
            "Create original music metadata for a YouTube video. Gemini produces text only; "
            "do not claim to create audio. Avoid imitating named artists, lyrics, melodies, "
            "or samples. Do not promise commercial rights or licensing. Return only JSON "
            "with music_prompt, title, alternate_title, description, tags (string array), "
            "thumbnail_prompt, seo_keywords (string array). Make titles meaningfully "
            "different for a sequential title test. Use relevant discovery keywords naturally, "
            "without claiming these are guaranteed trends. The music_prompt must be suitable "
            f"for an external audio generation service. Genre: {genre}. "
            f"Recent YouTube discovery signals: {keyword_context}."
        )
        response = self.session.post(
            "https://generativelanguage.googleapis.com/v1beta/"
            f"models/{self.model}:generateContent",
            params={"key": self.api_key},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json"},
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        try:
            data = json.loads(
                response.json()["candidates"][0]["content"]["parts"][0]["text"]
            )
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
            raise ValueError("Gemini returned invalid JSON metadata.") from error
        if not isinstance(data, dict):
            raise TypeError("Gemini response must be a JSON object.")
        return ContentMetadata.from_mapping(data)
