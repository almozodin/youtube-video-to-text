from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console

from transcriber.downloader import download_audio
from transcriber.exporters import (
    build_markdown_content,
    build_srt_content,
    build_txt_content,
    export_docx,
    export_markdown,
    export_srt,
    export_txt,
)
from transcriber.notion_sync import create_notion_page
from transcriber.obsidian_sync import sync_markdown_to_obsidian
from transcriber.utils import ensure_ffmpeg, iso_utc_now, sanitize_filename
from transcriber.whisper_engine import transcribe_audio

console = Console()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Transcribe a YouTube URL into multiple text formats.")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--model", default="base", choices=["tiny", "base", "small", "medium", "large-v3"])
    parser.add_argument("--language", default=None, help="Optional language code; auto-detected if omitted")
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--formats", nargs="+", default=["txt", "md"], choices=["txt", "md", "docx", "srt"])
    parser.add_argument("--keep-audio", action="store_true")
    parser.add_argument("--obsidian-vault", default=None)
    parser.add_argument("--notion", action="store_true")
    parser.add_argument("--notion-parent-page-id", default=None)
    parser.add_argument("--cookies", default=None, help="Path to cookies.txt for yt-dlp")
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    if not ensure_ffmpeg():
        raise SystemExit("ffmpeg is required but was not found in PATH.")

    output_root = Path(args.output_dir)
    download_root = Path("downloads")

    console.print("[cyan]Downloading audio from YouTube...[/cyan]")
    audio_path, metadata = download_audio(args.url, download_root, cookies=args.cookies)

    safe_title = sanitize_filename(metadata.title)
    final_output_dir = output_root / safe_title
    final_output_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"[cyan]Transcribing with model '{args.model}'...[/cyan]")
    segments, detected_language = transcribe_audio(audio_path, model_size=args.model, language=args.language)
    language = args.language or detected_language or metadata.language or "auto"
    created_iso = iso_utc_now()

    txt_content = build_txt_content(segments)
    md_content = build_markdown_content(metadata.title, metadata.webpage_url, created_iso, args.model, language, segments)
    srt_content = build_srt_content(segments)

    if "txt" in args.formats:
        export_txt(final_output_dir / "transcript.txt", txt_content)
    if "md" in args.formats:
        export_markdown(final_output_dir / "transcript.md", md_content)
    if "srt" in args.formats:
        export_srt(final_output_dir / "transcript.srt", srt_content)
    if "docx" in args.formats:
        export_docx(
            final_output_dir / "transcript.docx",
            metadata.title,
            metadata.webpage_url,
            created_iso,
            args.model,
            language,
            segments,
        )

    if args.keep_audio:
        shutil.copy2(audio_path, final_output_dir / "audio.mp3")

    if args.obsidian_vault:
        try:
            md_path = final_output_dir / "transcript.md"
            if not md_path.exists():
                export_markdown(md_path, md_content)
            synced_to = sync_markdown_to_obsidian(md_path, Path(args.obsidian_vault))
            console.print(f"[green]Synced markdown to Obsidian:[/green] {synced_to}")
        except Exception as exc:
            console.print(f"[yellow]Obsidian sync warning:[/yellow] {exc}")

    if args.notion:
        try:
            notion_url = create_notion_page(
                title=metadata.title,
                source_url=metadata.webpage_url,
                model=args.model,
                language=language,
                transcript_text=txt_content,
                parent_page_id=args.notion_parent_page_id,
            )
            console.print(f"[green]Notion page created:[/green] {notion_url}")
        except Exception as exc:
            console.print(f"[yellow]Notion sync warning:[/yellow] {exc}")

    if not args.keep_audio and audio_path.exists():
        audio_path.unlink()

    console.print(f"[green]Done. Output saved to:[/green] {final_output_dir}")


if __name__ == "__main__":
    main()
