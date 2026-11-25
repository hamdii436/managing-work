"""Vendor-neutral adapter for asynchronous music generation HTTP APIs.

Contract: POST {base_url}/jobs with {"prompt": "..."} returns {"id": "..."}.
GET {base_url}/jobs/{id} returns {"status": "running"} or, on success,
{"status": "completed", "audio_url": "https://..."}. Providers can be adapted
without changing the orchestration pipeline. This module does not generate audio.
"""

import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import requests


@dataclass(frozen=True)
class MusicJob:
    job_id: str
    status: str
    audio_url: str = ""


class HttpMusicProvider:
    def __init__(
        self,
        base_url: str,
        token: str = "",
        poll_interval_seconds: int = 10,
        timeout_seconds: int = 1800,
        session: requests.Session | None = None,
    ) -> None:
        parsed_base = urlparse(base_url)
        if (
            parsed_base.scheme != "https"
            or not parsed_base.netloc
            or parsed_base.username
            or parsed_base.password
        ):
            raise ValueError("MUSIC_API_URL must be an HTTPS URL without user info.")
        self.base_url = base_url.rstrip("/")
        self.poll_interval_seconds = poll_interval_seconds
        self.timeout_seconds = timeout_seconds
        self.session = session or requests.Session()
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def generate(self, prompt: str, output_path: Path) -> Path:
        response = self.session.post(
            f"{self.base_url}/jobs", json={"prompt": prompt}, timeout=30
        )
        response.raise_for_status()
        job_id = response.json().get("id")
        if not isinstance(job_id, str) or not job_id:
            raise ValueError("Music API submit response must include an id.")

        deadline = time.monotonic() + self.timeout_seconds
        while True:
            job = self._get_job(job_id)
            if job.status in {"completed", "complete", "succeeded"}:
                if not job.audio_url:
                    raise ValueError("Completed music job has no audio_url.")
                return self._download(job.audio_url, output_path)
            if job.status in {"failed", "cancelled", "canceled"}:
                raise RuntimeError(f"Music generation job {job_id} ended: {job.status}")
            if time.monotonic() >= deadline:
                raise TimeoutError(f"Music generation job {job_id} timed out.")
            time.sleep(self.poll_interval_seconds)

    def _get_job(self, job_id: str) -> MusicJob:
        response = self.session.get(f"{self.base_url}/jobs/{job_id}", timeout=30)
        response.raise_for_status()
        body = response.json()
        status = body.get("status")
        if not isinstance(status, str) or not status:
            raise ValueError("Music API status response must include status.")
        audio_url = body.get("audio_url", "")
        if not isinstance(audio_url, str):
            raise TypeError("Music API audio_url must be a string.")
        return MusicJob(job_id, status.lower(), audio_url)

    def _download(self, audio_url: str, output_path: Path) -> Path:
        parsed = urlparse(audio_url)
        if (
            parsed.scheme != "https"
            or not parsed.netloc
            or parsed.username
            or parsed.password
        ):
            raise ValueError(
                "Music API must return an HTTPS audio URL without user info."
            )
        response = self.session.get(audio_url, stream=True, timeout=120)
        response.raise_for_status()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("wb") as target:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    target.write(chunk)
        if output_path.stat().st_size == 0:
            output_path.unlink()
            raise ValueError("Music API returned an empty audio file.")
        return output_path
