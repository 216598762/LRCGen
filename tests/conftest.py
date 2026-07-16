"""Shared test fixtures for LRCGen tests."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def tmp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_metadata():
    """Return a sample AudioMetadata object."""
    from lrcgen.metadata import AudioMetadata

    return AudioMetadata(
        title="Test Song",
        artist="Test Artist",
        album="Test Album",
        duration=210.5,
        file_path=Path("/fake/song.mp3"),
    )


@pytest.fixture
def sample_synced_lrc():
    """Return sample synced LRC text from LRCLib."""
    return """[00:12.00]First line of lyrics
[00:15.30]Second line of lyrics
[00:18.50]Third line of lyrics"""


@pytest.fixture
def sample_plain_lyrics():
    """Return sample plain text lyrics from Genius."""
    return """First line of lyrics
Second line of lyrics
Third line of lyrics"""


@pytest.fixture
def sample_timestamps():
    """Return sample Whisper timestamps."""
    return [
        (12.0, 15.2),
        (15.3, 18.4),
        (18.5, 22.0),
    ]


@pytest.fixture
def create_minimal_mp3(tmp_dir):
    """Create a minimal valid MP3 file for testing.

    Returns a function that creates an MP3 file with given metadata.
    """
    from mutagen.mp3 import MP3
    from mutagen.id3 import TIT2, TPE1, TALB

    def _create_mp3(
        filename: str = "test.mp3",
        title: str | None = None,
        artist: str | None = None,
        album: str | None = None,
    ) -> Path:
        """Create a minimal MP3 file with ID3 tags."""
        filepath = tmp_dir / filename

        # Create a minimal MP3 file (silence)
        # MP3 frame header: 0xFF 0xFB (MPEG1, Layer3, 128kbps, 44100Hz, stereo)
        # Followed by zeros for the frame data
        frame_header = b"\xff\xfb\x90\x00"
        frame_data = b"\x00" * 413  # Standard MP3 frame size for 128kbps

        with open(filepath, "wb") as f:
            # Write a few frames of silence
            for _ in range(4):
                f.write(frame_header + frame_data)

        # Add ID3 tags if provided
        if title or artist or album:
            audio = MP3(str(filepath))
            audio.add_tags()
            if title:
                audio.tags.add(TIT2(encoding=3, text=[title]))
            if artist:
                audio.tags.add(TPE1(encoding=3, text=[artist]))
            if album:
                audio.tags.add(TALB(encoding=3, text=[album]))
            audio.save()

        return filepath

    return _create_mp3
