from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from transcriber.utils import sanitize_filename


@dataclass
class VideoMetadata:
    title: str
    uploader: str | None
    duration: int | None
    webpage_url: str
    upload_date: str | None
    language: str | None = None


def download_audio(url: str, download_root: Path, cookies: str | None = None) -> tuple[Path, VideoMetadata]:
    download_root.mkdir(parents=True, exist_ok=True)

    ydl_opts: dict[str, Any] = {
        "format": "bestaudio/best",
        "outtmpl": str(download_root / "%(title)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}
        ],
    }

    if cookies:
        ydl_opts["cookiefile"] = cookies

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get("title") or "Untitled Video"
            safe_title = sanitize_filename(video_title)
            expected_path = download_root / f"{video_title}.mp3"
            if not expected_path.exists():
                candidates = sorted(download_root.glob("*.mp3"), key=lambda p: p.stat().st_mtime, reverse=True)
                if not candidates:
                    raise RuntimeError("Audio download succeeded but mp3 file was not found.")
                expected_path = candidates[0]

            metadata = VideoMetadata(
                title=video_title,
                uploader=info.get("uploader"),
                duration=info.get("duration"),
                webpage_url=info.get("webpage_url") or url,
                upload_date=info.get("upload_date"),
                language=info.get("language"),
            )

            final_path = download_root / f"{safe_title}.mp3"
            if expected_path != final_path:
                expected_path.rename(final_path)
            return final_path, metadata
    except DownloadError as exc:
        message = str(exc)
        raise RuntimeError(f"Failed to download audio: {message}") from exc
