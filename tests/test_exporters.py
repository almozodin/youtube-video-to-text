from transcriber.exporters import build_markdown_content, build_srt_content
from transcriber.utils import format_timestamp, sanitize_filename
from dataclasses import dataclass


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str


def test_format_timestamp() -> None:
    assert format_timestamp(1.9) == "00:00:01"
    assert format_timestamp(3661) == "01:01:01"


def test_safe_filename() -> None:
    assert sanitize_filename("Example Video!!") == "example-video"
    assert sanitize_filename("   ") == "untitled-video"


def test_srt_export_format() -> None:
    segments = [TranscriptSegment(start=1.0, end=6.0, text="Hello"), TranscriptSegment(start=6.0, end=12.0, text="World")]
    srt = build_srt_content(segments)
    assert "1\n00:00:01,000 --> 00:00:06,000\nHello" in srt
    assert "2\n00:00:06,000 --> 00:00:12,000\nWorld" in srt


def test_markdown_export_content() -> None:
    segments = [TranscriptSegment(start=1.0, end=2.0, text="Sample line")]
    md = build_markdown_content(
        title="Example Video",
        source_url="https://www.youtube.com/watch?v=abc",
        created_iso="2026-01-01T00:00:00+00:00",
        model="base",
        language="en",
        segments=segments,
    )
    assert "title: \"Example Video\"" in md
    assert "## Transcript" in md
    assert "[00:00:01] Sample line" in md
