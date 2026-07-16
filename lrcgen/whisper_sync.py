"""Transcribe audio using faster-whisper for word-level timestamps."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from lrcgen.lrc_writer import format_lrc_timestamp

logger = logging.getLogger(__name__)


@dataclass
class WordTimestamp:
    """Timestamp for a single word."""

    word: str
    start: float  # seconds
    end: float  # seconds


@dataclass
class Segment:
    """A segment of transcribed audio."""

    text: str
    start: float  # seconds
    end: float  # seconds
    words: list[WordTimestamp]


def transcribe_audio(
    audio_path: Path,
    model_size: str = "small",
    device: str = "cpu",
    language: str | None = None,
) -> list[Segment]:
    """Transcribe audio file with word-level timestamps.

    Args:
        audio_path: Path to the audio file.
        model_size: Whisper model size (tiny, base, small, medium, large-v3).
        device: Device to run on (cpu, cuda).
        language: Optional language code (e.g., "en", "es").

    Returns:
        List of Segment objects with word timestamps.

    Raises:
        ImportError: If faster-whisper is not installed.
        RuntimeError: If transcription fails.
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise ImportError(
            "faster-whisper is required for audio transcription. "
            "Install it with: pip install faster-whisper"
        )

    logger.info(f"Loading Whisper model: {model_size} on {device}")
    model = WhisperModel(model_size, device=device, compute_type="int8")

    logger.info(f"Transcribing: {audio_path}")
    segments_gen, info = model.transcribe(
        str(audio_path),
        beam_size=5,
        word_timestamps=True,
        language=language,
    )

    logger.info(
        f"Detected language: {info.language} (probability: {info.language_probability:.2f})"
    )

    segments = []
    for seg in segments_gen:
        words = [
            WordTimestamp(
                word=w.word.strip(),
                start=w.start,
                end=w.end,
            )
            for w in (seg.words or [])
        ]

        segments.append(
            Segment(
                text=seg.text.strip(),
                start=seg.start,
                end=seg.end,
                words=words,
            )
        )

    logger.info(f"Transcribed {len(segments)} segments")
    return segments


def segments_to_lrc_lines(segments: list[Segment]) -> list[tuple[str, str]]:
    """Convert transcription segments to LRC timestamp lines.

    Args:
        segments: List of transcribed segments.

    Returns:
        List of (timestamp, text) tuples.
    """
    lines = []
    for seg in segments:
        timestamp = format_lrc_timestamp(seg.start)
        lines.append((timestamp, seg.text))
    return lines
