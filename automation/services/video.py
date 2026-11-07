"""Render a still-image MP4 video from generated audio using ffmpeg."""

import shutil
import subprocess
from pathlib import Path


class VideoRenderer:
    def __init__(self, ffmpeg_path: str = "ffmpeg") -> None:
        self.ffmpeg_path = ffmpeg_path

    def render(self, audio_path: Path, image_path: Path, output_path: Path) -> Path:
        executable = shutil.which(self.ffmpeg_path)
        if executable is None:
            raise RuntimeError(
                "ffmpeg was not found; install it and configure FFMPEG_PATH."
            )
        if not audio_path.is_file():
            raise FileNotFoundError(f"Audio file does not exist: {audio_path}")
        if not image_path.is_file():
            raise FileNotFoundError(f"Video image does not exist: {image_path}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        command = [
            executable,
            "-y",
            "-loop",
            "1",
            "-framerate",
            "30",
            "-i",
            str(image_path),
            "-i",
            str(audio_path),
            "-shortest",
            "-c:v",
            "libx264",
            "-tune",
            "stillimage",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-movflags",
            "+faststart",
            str(output_path),
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode:
            raise RuntimeError(
                f"ffmpeg failed to render video: {result.stderr[-1500:]}"
            )
        if not output_path.is_file() or output_path.stat().st_size == 0:
            raise RuntimeError("ffmpeg completed without producing a video file.")
        return output_path
