"""Generate LRC files from lyrics and metadata."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class LRCLine:
    """A single line in an LRC file."""
    timestamp: str  # [mm:ss.xx]
    text: str


@dataclass
class LRCFile:
    """Complete LRC file content."""
    title: str | None = None
    artist: str | None = None
    album: str | None = None
    length: str | None = None  # mm:ss format
    offset: int = 0  # milliseconds
    lines: list[LRCLine] | None = None


def create_lrc_from_synced(
    synced_lrc: str,
    title: str | None = None,
    artist: str | None = None,
    album: str | None = None,
    duration: float | None = None,
) -> str:
    """Create an LRC file from synced LRC text (from LRCLib).

    Args:
        synced_lrc: The synced LRC text from LRCLib.
        title: Song title.
        artist: Artist name.
        album: Album name.
        duration: Duration in seconds.

    Returns:
        Formatted LRC file content.
    """
    lines = []

    # Add metadata tags
    if title:
        lines.append(f"[ti:{title}]")
    if artist:
        lines.append(f"[ar:{artist}]")
    if album:
        lines.append(f"[al:{album}]")
    if duration:
        mins = int(duration // 60)
        secs = int(duration % 60)
        lines.append(f"[length:{mins:02d}:{secs:02d}]")

    lines.append("[by:LRCGen]")

    # Parse existing timestamps from synced LRC
    timestamp_pattern = re.compile(r"\[(\d{2}):(\d{2})\.(\d{2,3})\]")
    for line in synced_lrc.splitlines():
        match = timestamp_pattern.match(line.strip())
        if match:
            # Keep the timestamp line as-is
            lines.append(line.strip())
        elif line.strip():
            # Non-timestamp line, skip or handle
            continue

    return "\n".join(lines) + "\n"


def create_lrc_from_lines(
    timestamped_lines: list[tuple[str, str]],
    title: str | None = None,
    artist: str | None = None,
    album: str | None = None,
    duration: float | None = None,
) -> str:
    """Create an LRC file from timestamped lines.

    Args:
        timestamped_lines: List of (timestamp, text) tuples.
        title: Song title.
        artist: Artist name.
        album: Album name.
        duration: Duration in seconds.

    Returns:
        Formatted LRC file content.
    """
    lines = []

    # Add metadata tags
    if title:
        lines.append(f"[ti:{title}]")
    if artist:
        lines.append(f"[ar:{artist}]")
    if album:
        lines.append(f"[al:{album}]")
    if duration:
        mins = int(duration // 60)
        secs = int(duration % 60)
        lines.append(f"[length:{mins:02d}:{secs:02d}]")

    lines.append("[by:LRCGen]")

    # Add timestamped lyrics
    for timestamp, text in timestamped_lines:
        if text.strip():
            lines.append(f"{timestamp}{text}")

    return "\n".join(lines) + "\n"


def create_lrc_from_plain_text(
    plain_lyrics: str,
    timestamps: list[tuple[float, float]],
    title: str | None = None,
    artist: str | None = None,
    album: str | None = None,
    duration: float | None = None,
) -> str:
    """Create an LRC file from plain text lyrics and Whisper timestamps.

    This aligns plain text lyrics (from Genius) with timestamps from Whisper.

    Args:
        plain_lyrics: Plain text lyrics.
        timestamps: List of (start, end) timestamps from Whisper.
        title: Song title.
        artist: Artist name.
        album: Album name.
        duration: Duration in seconds.

    Returns:
        Formatted LRC file content.
    """
    # Split lyrics into lines
    lyric_lines = [line.strip() for line in plain_lyrics.splitlines() if line.strip()]

    # Match lines to timestamps
    timestamped = []
    for i, line in enumerate(lyric_lines):
        if i < len(timestamps):
            start = timestamps[i][0]
            timestamp = _format_lrc_timestamp(start)
            timestamped.append((timestamp, line))
        else:
            # No more timestamps, skip remaining lines
            break

    return create_lrc_from_lines(
        timestamped,
        title=title,
        artist=artist,
        album=album,
        duration=duration,
    )


def write_lrc_file(content: str, output_path: Path) -> Path:
    """Write LRC content to a file.

    Args:
        content: LRC file content.
        output_path: Path to write the LRC file.

    Returns:
        Path to the written file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    logger.info(f"Written LRC file: {output_path}")
    return output_path


def _format_lrc_timestamp(seconds: float) -> str:
    """Format seconds to LRC timestamp [mm:ss.xx]."""
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"[{minutes:02d}:{secs:05.2f}]"
