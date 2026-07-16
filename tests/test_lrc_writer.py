"""Tests for lrcgen.lrc_writer module."""

from __future__ import annotations

from lrcgen.lrc_writer import (
    create_lrc_from_lines,
    create_lrc_from_plain_text,
    create_lrc_from_synced,
    format_lrc_timestamp,
    write_lrc_file,
)


class TestFormatLrcTimestamp:
    """Tests for format_lrc_timestamp function."""

    def test_zero_seconds(self):
        """Zero seconds formats correctly."""
        assert format_lrc_timestamp(0.0) == "[00:00.00]"

    def test_seconds_only(self):
        """Seconds less than a minute format correctly."""
        assert format_lrc_timestamp(45.5) == "[00:45.50]"

    def test_minutes_and_seconds(self):
        """Minutes and seconds format correctly."""
        assert format_lrc_timestamp(125.75) == "[02:05.75]"

    def test_exact_minute(self):
        """Exact minute boundaries format correctly."""
        assert format_lrc_timestamp(60.0) == "[01:00.00]"

    def test_large_values(self):
        """Large time values format correctly."""
        assert format_lrc_timestamp(3661.5) == "[61:01.50]"

    def test_fractional_seconds(self):
        """Fractional seconds round correctly."""
        assert format_lrc_timestamp(10.123) == "[00:10.12]"


class TestCreateLrcFromSynced:
    """Tests for create_lrc_from_synced function."""

    def test_basic_synced_lyrics(self):
        """Parse basic synced LRC text."""
        synced = """[00:12.00]First line
[00:15.30]Second line"""
        result = create_lrc_from_synced(synced)

        assert "[by:LRCGen]" in result
        assert "[00:12.00]First line" in result
        assert "[00:15.30]Second line" in result

    def test_with_metadata(self):
        """Include metadata tags when provided."""
        synced = "[00:10.00]Hello"
        result = create_lrc_from_synced(
            synced,
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            duration=210.0,
        )

        assert "[ti:Test Song]" in result
        assert "[ar:Test Artist]" in result
        assert "[al:Test Album]" in result
        assert "[length:03:30]" in result

    def test_empty_lyrics(self):
        """Handle empty synced lyrics gracefully."""
        result = create_lrc_from_synced("", title="Empty")
        assert "[ti:Empty]" in result
        assert "[by:LRCGen]" in result

    def test_non_timestamp_lines_skipped(self):
        """Non-timestamp lines are skipped."""
        synced = """[Some Header]
[00:10.00]Lyric line
[Chorus]
[00:15.00]Another line"""
        result = create_lrc_from_synced(synced)

        assert "[Some Header]" not in result
        assert "[Chorus]" not in result
        assert "[00:10.00]Lyric line" in result
        assert "[00:15.00]Another line" in result


class TestCreateLrcFromLines:
    """Tests for create_lrc_from_lines function."""

    def test_basic_timestamped_lines(self):
        """Create LRC from timestamped line tuples."""
        lines = [
            ("[00:12.00]", "First line"),
            ("[00:15.30]", "Second line"),
        ]
        result = create_lrc_from_lines(lines)

        assert "[00:12.00]First line" in result
        assert "[00:15.30]Second line" in result
        assert "[by:LRCGen]" in result

    def test_empty_text_filtered(self):
        """Lines with empty text are filtered out."""
        lines = [
            ("[00:12.00]", "Valid line"),
            ("[00:15.30]", ""),
            ("[00:18.00]", "   "),
            ("[00:20.00]", "Another valid"),
        ]
        result = create_lrc_from_lines(lines)

        assert "[00:12.00]Valid line" in result
        assert "[00:20.00]Another valid" in result
        # Empty lines should not appear
        assert result.count("[00:15.30]") == 0
        assert result.count("[00:18.00]") == 0

    def test_with_metadata(self):
        """Include metadata tags when provided."""
        lines = [("[00:10.00]", "Hello")]
        result = create_lrc_from_lines(
            lines,
            title="My Song",
            artist="My Artist",
        )

        assert "[ti:My Song]" in result
        assert "[ar:My Artist]" in result


class TestCreateLrcFromPlainText:
    """Tests for create_lrc_from_plain_text function."""

    def test_align_lyrics_with_timestamps(self):
        """Align plain text lyrics with Whisper timestamps."""
        lyrics = "Line one\nLine two\nLine three"
        timestamps = [(10.0, 15.0), (15.5, 20.0), (20.5, 25.0)]

        result = create_lrc_from_plain_text(lyrics, timestamps)

        assert "[00:10.00]Line one" in result
        assert "[00:15.50]Line two" in result
        assert "[00:20.50]Line three" in result

    def test_fewer_timestamps_than_lines(self):
        """Drop extra lines when timestamps run out."""
        lyrics = "Line one\nLine two\nLine three\nLine four"
        timestamps = [(10.0, 15.0), (15.5, 20.0)]

        result = create_lrc_from_plain_text(lyrics, timestamps)

        assert "[00:10.00]Line one" in result
        assert "[00:15.50]Line two" in result
        assert "Line three" not in result
        assert "Line four" not in result

    def test_fewer_lines_than_timestamps(self):
        """Use all lines when there are more timestamps."""
        lyrics = "Line one\nLine two"
        timestamps = [(10.0, 15.0), (15.5, 20.0), (20.5, 25.0)]

        result = create_lrc_from_plain_text(lyrics, timestamps)

        assert "[00:10.00]Line one" in result
        assert "[00:15.50]Line two" in result
        # Third timestamp has no corresponding line
        assert result.count("[00:20.50]") == 0

    def test_empty_lyrics(self):
        """Handle empty lyrics gracefully."""
        lyrics = ""
        timestamps = [(10.0, 15.0)]

        result = create_lrc_from_plain_text(lyrics, timestamps)

        assert "[by:LRCGen]" in result
        assert "[00:10.00]" not in result

    def test_empty_timestamps(self):
        """Handle empty timestamps gracefully."""
        lyrics = "Line one\nLine two"
        timestamps = []

        result = create_lrc_from_plain_text(lyrics, timestamps)

        assert "[by:LRCGen]" in result
        assert "Line one" not in result


class TestWriteLrcFile:
    """Tests for write_lrc_file function."""

    def test_write_creates_file(self, tmp_path):
        """Write LRC content to a new file."""
        content = "[by:LRCGen]\n[00:10.00]Hello\n"
        output = tmp_path / "test.lrc"

        result = write_lrc_file(content, output)

        assert result == output
        assert output.exists()
        assert output.read_text(encoding="utf-8") == content

    def test_write_creates_parent_dirs(self, tmp_path):
        """Write LRC file creates parent directories if needed."""
        content = "[by:LRCGen]\n"
        output = tmp_path / "subdir" / "nested" / "test.lrc"

        result = write_lrc_file(content, output)

        assert output.exists()
        assert result == output

    def test_write_overwrites_existing(self, tmp_path):
        """Write LRC file overwrites existing file."""
        output = tmp_path / "test.lrc"
        output.write_text("old content")

        content = "[by:LRCGen]\n[00:10.00]New content\n"
        write_lrc_file(content, output)

        assert output.read_text(encoding="utf-8") == content
