from __future__ import annotations

import shutil
from pathlib import Path

from transcriber.utils import resolve_non_overwriting_path


def sync_markdown_to_obsidian(markdown_path: Path, vault_path: Path) -> Path:
    if not vault_path.exists() or not vault_path.is_dir():
        raise ValueError(f"Invalid Obsidian vault path: {vault_path}")

    destination_dir = vault_path / "YouTube Transcripts"
    destination_dir.mkdir(parents=True, exist_ok=True)

    destination = resolve_non_overwriting_path(destination_dir / markdown_path.name)
    shutil.copy2(markdown_path, destination)
    return destination
