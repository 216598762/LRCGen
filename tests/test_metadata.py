"""Tests for lrcgen.metadata module."""

from __future__ import annotations

from pathlib import Path

import pytest

from lrcgen.metadata import (
    AudioMetadata,
    SUPPORTED_EXTENSIONS,
    extract_metadata,
    is_supported_audio,
)


class TestAudioMetadata:
    """Tests for the AudioMetadata dataclass."""

    def test_search_query_with_artist_and_title(self):
        """Search query combines artist and title."""
        meta = AudioMetadata(
            title="Bohemian Rhapsody",
            artist="Queen",
            album="A Night at the Opera",
            duration=354.0,
            file_path=Path("/music/song.mp3"),
        )
        assert meta.search_query == "Queen Bohemian Rhapsody"

    def test_search_query_title_only(self):
        """Search query uses title when artist is missing."""
        meta = AudioMetadata(
            title="Bohemian Rhapsody",
            artist=None,
            album=None,
            duration=354.0,
            file_path=Path("/music/song.mp3"),
        )
        assert meta.search_query == "Bohemian Rhapsody"

    def test_search_query_artist_only(self):
        """Search query uses artist when title is missing."""
        meta = AudioMetadata(
            title=None,
            artist="Queen",
            album=None,
            duration=354.0,
            file_path=Path("/music/song.mp3"),
        )
        assert meta.search_query == "Queen"

    def test_search_query_fallback_to_filename(self):
        """Search query falls back to filename stem when no metadata."""
        meta = AudioMetadata(
            title=None,
            artist=None,
            album=None,
            duration=354.0,
            file_path=Path("/music/bohemian_rhapsody.mp3"),
        )
        assert meta.search_query == "bohemian_rhapsody"

    def test_is_complete_true(self):
        """is_complete returns True when both title and artist exist."""
        meta = AudioMetadata(
            title="Song",
            artist="Artist",
            album=None,
            duration=None,
            file_path=Path("/song.mp3"),
        )
        assert meta.is_complete is True

    def test_is_complete_false_missing_title(self):
        """is_complete returns False when title is missing."""
        meta = AudioMetadata(
            title=None,
            artist="Artist",
            album=None,
            duration=None,
            file_path=Path("/song.mp3"),
        )
        assert meta.is_complete is False

    def test_is_complete_false_missing_artist(self):
        """is_complete returns False when artist is missing."""
        meta = AudioMetadata(
            title="Song",
            artist=None,
            album=None,
            duration=None,
            file_path=Path("/song.mp3"),
        )
        assert meta.is_complete is False


class TestIsSupportedAudio:
    """Tests for is_supported_audio function."""

    @pytest.mark.parametrize("ext", sorted(SUPPORTED_EXTENSIONS))
    def test_supported_extensions(self, ext):
        """All listed extensions should be supported."""
        assert is_supported_audio(Path(f"song{ext}")) is True

    @pytest.mark.parametrize("ext", [".txt", ".pdf", ".jpg", ".py", ".json", ""])
    def test_unsupported_extensions(self, ext):
        """Unsupported extensions should return False."""
        assert is_supported_audio(Path(f"file{ext}")) is False

    def test_case_insensitive(self):
        """Extension check should be case-insensitive."""
        assert is_supported_audio(Path("song.MP3")) is True
        assert is_supported_audio(Path("song.Flac")) is True
        assert is_supported_audio(Path("song.OGG")) is True


class TestExtractMetadata:
    """Tests for extract_metadata function."""

    def test_file_not_found(self):
        """Raises FileNotFoundError for missing files."""
        with pytest.raises(FileNotFoundError, match="Audio file not found"):
            extract_metadata(Path("/nonexistent/song.mp3"))

    def test_unsupported_format(self):
        """Raises ValueError for unsupported file formats."""
        # Create a dummy file with unsupported extension
        tmpfile = Path("/tmp/test.txt")
        tmpfile.write_text("dummy")
        try:
            with pytest.raises(ValueError, match="Unsupported audio format"):
                extract_metadata(tmpfile)
        finally:
            tmpfile.unlink()

    def test_extract_from_mp3(self, create_minimal_mp3):
        """Extract metadata from an MP3 file with ID3 tags."""
        filepath = create_minimal_mp3(
            filename="tagged.mp3",
            title="My Song",
            artist="My Artist",
            album="My Album",
        )
        meta = extract_metadata(filepath)

        assert meta.title == "My Song"
        assert meta.artist == "My Artist"
        assert meta.album == "My Album"
        assert meta.file_path == filepath
        assert meta.duration is not None
        assert meta.duration > 0

    def test_extract_from_untagged_mp3(self, create_minimal_mp3):
        """Extract metadata from an MP3 file without tags."""
        filepath = create_minimal_mp3(filename="untagged.mp3")
        meta = extract_metadata(filepath)

        assert meta.title is None
        assert meta.artist is None
        assert meta.album is None
        assert meta.file_path == filepath
        assert meta.duration is not None
