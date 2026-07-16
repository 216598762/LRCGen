"""Tests for lrcgen.whisper_sync module."""

from __future__ import annotations

import pytest

from lrcgen.whisper_sync import Segment, WordTimestamp, segments_to_lrc_lines


class TestSegmentsToLrcLines:
    """Tests for segments_to_lrc_lines function."""

    def test_single_segment(self):
        """Convert a single segment to LRC line."""
        segments = [
            Segment(
                text="Hello world",
                start=10.5,
                end=12.0,
                words=[],
            )
        ]
        result = segments_to_lrc_lines(segments)

        assert len(result) == 1
        assert result[0] == ("[00:10.50]", "Hello world")

    def test_multiple_segments(self):
        """Convert multiple segments to LRC lines."""
        segments = [
            Segment(text="First line", start=5.0, end=8.0, words=[]),
            Segment(text="Second line", start=12.5, end=15.0, words=[]),
            Segment(text="Third line", start=20.0, end=23.5, words=[]),
        ]
        result = segments_to_lrc_lines(segments)

        assert len(result) == 3
        assert result[0] == ("[00:05.00]", "First line")
        assert result[1] == ("[00:12.50]", "Second line")
        assert result[2] == ("[00:20.00]", "Third line")

    def test_empty_segments(self):
        """Handle empty segments list."""
        result = segments_to_lrc_lines([])
        assert result == []

    def test_timestamp_format(self):
        """Verify LRC timestamp format [mm:ss.xx]."""
        segments = [
            Segment(text="Test", start=125.75, end=130.0, words=[]),
        ]
        result = segments_to_lrc_lines(segments)

        assert result[0][0] == "[02:05.75]"

    def test_preserves_segment_text(self):
        """Verify segment text is preserved exactly."""
        text = "This is a test with special chars: !@#$%"
        segments = [
            Segment(text=text, start=0.0, end=5.0, words=[]),
        ]
        result = segments_to_lrc_lines(segments)

        assert result[0][1] == text

    def test_words_ignored(self):
        """Words field is not used in output (only text)."""
        segments = [
            Segment(
                text="Hello",
                start=1.0,
                end=2.0,
                words=[
                    WordTimestamp(word="Hello", start=1.0, end=2.0),
                ],
            )
        ]
        result = segments_to_lrc_lines(segments)

        assert result[0] == ("[00:01.00]", "Hello")

    def test_large_timestamp(self):
        """Handle timestamps over 60 minutes."""
        segments = [
            Segment(text="Long song", start=3725.0, end=3730.0, words=[]),
        ]
        result = segments_to_lrc_lines(segments)

        assert result[0][0] == "[62:05.00]"
