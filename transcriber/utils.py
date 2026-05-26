from __future__ import annotations

import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


def ensure_ffmpeg() -> bool:
    """Return True when ffmpeg is available in PATH."""
    return shutil.which("ffmpeg") is not None


def sanitize_filename(name: str) -> str:
    """Create a safe, lowercase slug for file/folder naming."""
    cleaned = re.sub(r"[^a-zA-Z0-9\s-]", "", name).strip().lower()
    slug = re.sub(r"[\s_-]+", "-", cleaned).strip("-")
    return slug or "untitled-video"


def format_timestamp(seconds: float) -> str:
    total_seconds = int(max(seconds, 0))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_srt_timestamp(seconds: float) -> str:
    ms_total = int(round(max(seconds, 0) * 1000))
    hours, remainder = divmod(ms_total, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, ms = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


def iso_utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def resolve_non_overwriting_path(path: Path) -> Path:
    if not path.exists():
        return path

    stem, suffix = path.stem, path.suffix
    counter = 1
    while True:
        candidate = path.with_name(f"{stem}-{counter}{suffix}")
        if not candidate.exists():
            return candidate
        counter += 1
