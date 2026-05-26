from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from faster_whisper import WhisperModel


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str


def transcribe_audio(
    audio_path: Path,
    model_size: str = "base",
    language: str | None = None,
    device: str = "cpu",
    compute_type: str = "int8",
) -> tuple[list[TranscriptSegment], str | None]:
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    segments, info = model.transcribe(str(audio_path), language=language)
    result = [
        TranscriptSegment(start=segment.start, end=segment.end, text=segment.text.strip())
        for segment in segments
    ]
    detected_language = getattr(info, "language", None)
    return result, detected_language
