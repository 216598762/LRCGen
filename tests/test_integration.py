"""Integration tests for LRCGen processing pipeline.

These tests exercise the full pipeline from audio file to LRC output,
using real files but mocked external services (LRCLib, Genius, Whisper).
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from lrcgen.lyrics_search import LyricsResult
from lrcgen.metadata import extract_metadata
from lrcgen.whisper_sync import Segment, WordTimestamp
from lrcgen.lrc_writer import (
    create_lrc_from_lines,
    create_lrc_from_plain_text,
    create_lrc_from_synced,
    write_lrc_file,
)


@pytest.fixture
def tagged_mp3(create_minimal_mp3):
    """Create a tagged MP3 file for integration testing."""
    return create_minimal_mp3(
        filename="test_song.mp3",
        title="Test Song",
        artist="Test Artist",
        album="Test Album",
    )


@pytest.fixture
def sample_segments():
    """Return sample Whisper transcription segments."""
    return [
        Segment(
            text="First line of lyrics",
            start=5.0,
            end=8.0,
            words=[
                WordTimestamp(word="First", start=5.0, end=5.5),
                WordTimestamp(word="line", start=5.5, end=6.0),
                WordTimestamp(word="of", start=6.0, end=6.2),
                WordTimestamp(word="lyrics", start=6.2, end=8.0),
            ],
        ),
        Segment(
            text="Second line of lyrics",
            start=10.0,
            end=13.5,
            words=[
                WordTimestamp(word="Second", start=10.0, end=10.5),
                WordTimestamp(word="line", start=10.5, end=11.0),
                WordTimestamp(word="of", start=11.0, end=11.2),
                WordTimestamp(word="lyrics", start=11.2, end=13.5),
            ],
        ),
        Segment(
            text="Third line of lyrics",
            start=15.0,
            end=18.0,
            words=[
                WordTimestamp(word="Third", start=15.0, end=15.5),
                WordTimestamp(word="line", start=15.5, end=16.0),
                WordTimestamp(word="of", start=16.0, end=16.2),
                WordTimestamp(word="lyrics", start=16.2, end=18.0),
            ],
        ),
    ]


class TestEndToEndWithSyncedLyrics:
    """Integration test: LRCLib provides synced lyrics."""

    def test_full_pipeline_synced(self, tagged_mp3, tmp_path):
        """Process MP3 with synced lyrics from LRCLib."""
        synced_lrc = """[00:05.00]First line of lyrics
[00:10.00]Second line of lyrics
[00:15.00]Third line of lyrics"""

        mock_result = LyricsResult(
            lyrics="First line of lyrics\nSecond line of lyrics\nThird line of lyrics",
            synced_lyrics=synced_lrc,
            source="lrclib",
            title="Test Song",
            artist="Test Artist",
        )

        with patch("lrcgen.cli.search_lyrics", return_value=mock_result):
            from lrcgen.cli import process_audio_file

            success = process_audio_file(
                audio_path=tagged_mp3,
                model_size="tiny",
                device="cpu",
                genius_token=None,
                output_dir=None,
                force=True,
                language=None,
            )

        assert success is True

        # Verify LRC file was created
        lrc_path = tagged_mp3.with_suffix(".lrc")
        assert lrc_path.exists()

        # Verify LRC content
        content = lrc_path.read_text(encoding="utf-8")
        assert "[ti:Test Song]" in content
        assert "[ar:Test Artist]" in content
        assert "[al:Test Album]" in content
        assert "[by:LRCGen]" in content
        assert "[00:05.00]First line of lyrics" in content
        assert "[00:10.00]Second line of lyrics" in content
        assert "[00:15.00]Third line of lyrics" in content


class TestEndToEndWithGeniusLyrics:
    """Integration test: Genius provides plain text, Whisper provides timestamps."""

    def test_full_pipeline_genius_whisper(self, tagged_mp3, sample_segments):
        """Process MP3 with Genius lyrics aligned with Whisper timestamps."""
        genius_result = LyricsResult(
            lyrics="First line of lyrics\nSecond line of lyrics\nThird line of lyrics",
            synced_lyrics=None,
            source="genius",
            title="Test Song",
            artist="Test Artist",
        )

        with patch("lrcgen.cli.search_lyrics", return_value=genius_result), \
             patch("lrcgen.cli.transcribe_audio", return_value=sample_segments):
            from lrcgen.cli import process_audio_file

            success = process_audio_file(
                audio_path=tagged_mp3,
                model_size="tiny",
                device="cpu",
                genius_token="test_token",
                output_dir=None,
                force=True,
                language=None,
            )

        assert success is True

        # Verify LRC file was created
        lrc_path = tagged_mp3.with_suffix(".lrc")
        assert lrc_path.exists()

        # Verify LRC content has timestamps from Whisper
        content = lrc_path.read_text(encoding="utf-8")
        assert "[ti:Test Song]" in content
        assert "[ar:Test Artist]" in content
        assert "[00:05.00]First line of lyrics" in content
        assert "[00:10.00]Second line of lyrics" in content
        assert "[00:15.00]Third line of lyrics" in content


class TestEndToEndWithWhisperOnly:
    """Integration test: No lyrics found, use Whisper transcription directly."""

    def test_full_pipeline_whisper_only(self, tagged_mp3, sample_segments):
        """Process MP3 with only Whisper transcription (no lyrics sources)."""
        with patch("lrcgen.cli.search_lyrics", return_value=None), \
             patch("lrcgen.cli.transcribe_audio", return_value=sample_segments):
            from lrcgen.cli import process_audio_file

            success = process_audio_file(
                audio_path=tagged_mp3,
                model_size="tiny",
                device="cpu",
                genius_token=None,
                output_dir=None,
                force=True,
                language=None,
            )

        assert success is True

        # Verify LRC file was created
        lrc_path = tagged_mp3.with_suffix(".lrc")
        assert lrc_path.exists()

        # Verify LRC content
        content = lrc_path.read_text(encoding="utf-8")
        assert "[ti:Test Song]" in content
        assert "[ar:Test Artist]" in content
        assert "[00:05.00]First line of lyrics" in content
        assert "[00:10.00]Second line of lyrics" in content
        assert "[00:15.00]Third line of lyrics" in content


class TestEndToEndEdgeCases:
    """Integration test edge cases."""

    def test_skip_existing_lrc(self, tagged_mp3):
        """Skip processing when LRC file already exists."""
        lrc_path = tagged_mp3.with_suffix(".lrc")
        lrc_path.write_text("[by:LRCGen]\n[00:10.00]Existing content\n")

        with patch("lrcgen.cli.search_lyrics") as mock_search:
            from lrcgen.cli import process_audio_file

            success = process_audio_file(
                audio_path=tagged_mp3,
                model_size="tiny",
                device="cpu",
                genius_token=None,
                output_dir=None,
                force=False,  # Don't force
                language=None,
            )

        assert success is True
        # Should not have called search_lyrics (skipped)
        mock_search.assert_not_called()
        # Original content preserved
        assert "Existing content" in lrc_path.read_text()

    def test_force_overwrite(self, tagged_mp3):
        """Force overwrite existing LRC file."""
        lrc_path = tagged_mp3.with_suffix(".lrc")
        lrc_path.write_text("[by:LRCGen]\n[00:10.00]Old content\n")

        mock_result = LyricsResult(
            lyrics="New lyrics",
            synced_lyrics="[00:05.00]New lyrics",
            source="lrclib",
        )

        with patch("lrcgen.cli.search_lyrics", return_value=mock_result):
            from lrcgen.cli import process_audio_file

            success = process_audio_file(
                audio_path=tagged_mp3,
                model_size="tiny",
                device="cpu",
                genius_token=None,
                output_dir=None,
                force=True,  # Force overwrite
                language=None,
            )

        assert success is True
        content = lrc_path.read_text()
        assert "New lyrics" in content
        assert "Old content" not in content

    def test_output_directory(self, tagged_mp3, tmp_path):
        """Write LRC to specified output directory."""
        output_dir = tmp_path / "lrc_output"

        mock_result = LyricsResult(
            lyrics="Test lyrics",
            synced_lyrics="[00:05.00]Test lyrics",
            source="lrclib",
        )

        with patch("lrcgen.cli.search_lyrics", return_value=mock_result):
            from lrcgen.cli import process_audio_file

            success = process_audio_file(
                audio_path=tagged_mp3,
                model_size="tiny",
                device="cpu",
                genius_token=None,
                output_dir=output_dir,
                force=True,
                language=None,
            )

        assert success is True
        lrc_path = output_dir / "test_song.lrc"
        assert lrc_path.exists()

    def test_whisper_returns_no_segments(self, tagged_mp3):
        """Handle case when Whisper returns no segments."""
        genius_result = LyricsResult(
            lyrics="Some lyrics",
            synced_lyrics=None,
            source="genius",
        )

        with patch("lrcgen.cli.search_lyrics", return_value=genius_result), \
             patch("lrcgen.cli.transcribe_audio", return_value=[]):
            from lrcgen.cli import process_audio_file

            success = process_audio_file(
                audio_path=tagged_mp3,
                model_size="tiny",
                device="cpu",
                genius_token="test_token",
                output_dir=None,
                force=True,
                language=None,
            )

        assert success is False
        # No LRC file should be created
        assert not tagged_mp3.with_suffix(".lrc").exists()

    def test_metadata_extraction_integration(self, tagged_mp3):
        """Verify metadata extraction works with real file."""
        metadata = extract_metadata(tagged_mp3)

        assert metadata.title == "Test Song"
        assert metadata.artist == "Test Artist"
        assert metadata.album == "Test Album"
        assert metadata.duration is not None
        assert metadata.duration > 0
        assert metadata.file_path == tagged_mp3
        assert metadata.is_complete is True
        assert metadata.search_query == "Test Artist Test Song"

    def test_metadata_extraction_failure(self, tagged_mp3):
        """Handle case when metadata extraction raises an exception."""
        with patch("lrcgen.cli.extract_metadata", side_effect=Exception("Corrupt file")):
            from lrcgen.cli import process_audio_file

            success = process_audio_file(
                audio_path=tagged_mp3,
                model_size="tiny",
                device="cpu",
                genius_token=None,
                output_dir=None,
                force=True,
                language=None,
            )

        assert success is False
        # No LRC file should be created
        assert not tagged_mp3.with_suffix(".lrc").exists()

    def test_whisper_exception(self, tagged_mp3):
        """Handle case when Whisper transcription raises an exception."""
        with patch("lrcgen.cli.search_lyrics", return_value=None), \
             patch("lrcgen.cli.transcribe_audio", side_effect=RuntimeError("Model load failed")):
            from lrcgen.cli import process_audio_file

            success = process_audio_file(
                audio_path=tagged_mp3,
                model_size="tiny",
                device="cpu",
                genius_token=None,
                output_dir=None,
                force=True,
                language=None,
            )

        assert success is False
        # No LRC file should be created
        assert not tagged_mp3.with_suffix(".lrc").exists()


class TestEndToEndLRCContent:
    """Integration test verifying LRC file format and content."""

    def test_lrc_format_valid(self, tagged_mp3):
        """Verify generated LRC file has valid format."""
        synced_lrc = """[00:01.00]Line one
[00:05.50]Line two
[00:10.25]Line three"""

        mock_result = LyricsResult(
            lyrics="Line one\nLine two\nLine three",
            synced_lyrics=synced_lrc,
            source="lrclib",
            title="Format Test",
            artist="Test Artist",
        )

        with patch("lrcgen.cli.search_lyrics", return_value=mock_result):
            from lrcgen.cli import process_audio_file

            process_audio_file(
                audio_path=tagged_mp3,
                model_size="tiny",
                device="cpu",
                genius_token=None,
                output_dir=None,
                force=True,
                language=None,
            )

        content = tagged_mp3.with_suffix(".lrc").read_text(encoding="utf-8")
        lines = content.strip().split("\n")

        # Verify metadata tags are present
        assert "[ti:Test Song]" in lines
        assert "[ar:Test Artist]" in lines
        assert "[al:Test Album]" in lines
        assert "[by:LRCGen]" in lines
        # Verify timestamped lyrics are present
        assert "[00:01.00]Line one" in lines
        assert "[00:05.50]Line two" in lines
        assert "[00:10.25]Line three" in lines
