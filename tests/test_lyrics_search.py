"""Tests for lrcgen.lyrics_search module with mocked HTTP responses."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from lrcgen.lyrics_search import (
    LyricsResult,
    search_genius,
    search_lrclib,
    search_lyrics,
)
from lrcgen.metadata import AudioMetadata


@pytest.fixture
def sample_metadata():
    """Return a sample AudioMetadata object for testing."""
    return AudioMetadata(
        title="Bohemian Rhapsody",
        artist="Queen",
        album="A Night at the Opera",
        duration=354.0,
        file_path=Path("/music/song.mp3"),
    )


class TestLyricsResult:
    """Tests for LyricsResult dataclass."""

    def test_basic_creation(self):
        """Create a LyricsResult with required fields."""
        result = LyricsResult(
            lyrics="Test lyrics",
            synced_lyrics=None,
            source="lrclib",
        )
        assert result.lyrics == "Test lyrics"
        assert result.synced_lyrics is None
        assert result.source == "lrclib"
        assert result.title is None
        assert result.artist is None

    def test_with_optional_fields(self):
        """Create a LyricsResult with all fields."""
        result = LyricsResult(
            lyrics="Test lyrics",
            synced_lyrics="[00:10.00]Test",
            source="genius",
            title="Test Song",
            artist="Test Artist",
        )
        assert result.title == "Test Song"
        assert result.artist == "Test Artist"
        assert result.synced_lyrics == "[00:10.00]Test"


class TestSearchLrclib:
    """Tests for search_lrclib function."""

    def test_successful_search(self, sample_metadata):
        """Return LyricsResult when LRCLib finds results."""
        mock_response_data = [
            {
                "id": 12345,
                "trackName": "Bohemian Rhapsody",
                "artistName": "Queen",
                "albumName": "A Night at the Opera",
                "duration": 354,
                "syncedLyrics": "[00:00.00]Is this the real life?\n[00:03.50]Is this just fantasy?",
                "plainLyrics": "Is this the real life?\nIs this just fantasy?",
            }
        ]
        with patch("lrcgen.lyrics_search.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = search_lrclib(sample_metadata)

            assert result is not None
            assert result.source == "lrclib"
            assert result.lyrics == "Is this the real life?\nIs this just fantasy?"
            assert result.synced_lyrics is not None
            assert "[00:00.00]" in result.synced_lyrics
            assert result.title == "Bohemian Rhapsody"
            assert result.artist == "Queen"
            mock_response.raise_for_status.assert_called_once()

    def test_no_results(self, sample_metadata):
        """Return None when LRCLib returns empty results."""
        with patch("lrcgen.lyrics_search.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = []
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = search_lrclib(sample_metadata)
            assert result is None

    def test_plain_lyrics_only(self, sample_metadata):
        """Return LyricsResult with synced_lyrics=None when only plainLyrics available."""
        mock_response_data = [
            {
                "id": 12345,
                "trackName": "Bohemian Rhapsody",
                "artistName": "Queen",
                "albumName": "A Night at the Opera",
                "duration": 354,
                "syncedLyrics": None,
                "plainLyrics": "Is this the real life?\nIs this just fantasy?",
            }
        ]
        with patch("lrcgen.lyrics_search.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = search_lrclib(sample_metadata)

            assert result is not None
            assert result.source == "lrclib"
            assert result.lyrics == "Is this the real life?\nIs this just fantasy?"
            assert result.synced_lyrics is None
            assert result.title == "Bohemian Rhapsody"
            assert result.artist == "Queen"

    def test_no_metadata(self):
        """Return None when no metadata is provided."""
        metadata = AudioMetadata(
            title=None,
            artist=None,
            album=None,
            duration=None,
            file_path=Path("/fake.mp3"),
        )
        result = search_lrclib(metadata)
        assert result is None

    def test_request_exception(self, sample_metadata):
        """Return None when request fails."""
        import requests
        with patch("lrcgen.lyrics_search.requests.get") as mock_get:
            mock_get.side_effect = requests.RequestException("Connection error")

            result = search_lrclib(sample_metadata)
            assert result is None

    def test_builds_correct_params(self, sample_metadata):
        """Build correct search parameters from metadata."""
        with patch("lrcgen.lyrics_search.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = []
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            search_lrclib(sample_metadata)

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            params = call_args[1]["params"]
            assert params["track_name"] == "Bohemian Rhapsody"
            assert params["artist_name"] == "Queen"
            assert params["album_name"] == "A Night at the Opera"
            assert params["duration"] == "354"

    def test_only_title_param(self):
        """Build params with only title when other fields missing."""
        metadata = AudioMetadata(
            title="Test Song",
            artist=None,
            album=None,
            duration=None,
            file_path=Path("/fake.mp3"),
        )
        with patch("lrcgen.lyrics_search.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = []
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            search_lrclib(metadata)

            params = mock_get.call_args[1]["params"]
            assert "track_name" in params
            assert "artist_name" not in params


class TestSearchGenius:
    """Tests for search_genius function."""

    def test_no_token(self, sample_metadata):
        """Return None when no Genius token is provided."""
        result = search_genius(sample_metadata, genius_token=None)
        assert result is None

    def test_successful_search(self, sample_metadata):
        """Return LyricsResult when Genius finds results."""
        mock_song = MagicMock()
        mock_song.lyrics = "Is this the real life?\nIs this just fantasy?"
        mock_song.title = "Bohemian Rhapsody"
        mock_song.artist = "Queen"

        with patch("lyricsgenius.Genius") as MockGenius:
            mock_genius = MagicMock()
            mock_genius.search_song.return_value = mock_song
            MockGenius.return_value = mock_genius

            result = search_genius(sample_metadata, genius_token="test_token")

            assert result is not None
            assert result.source == "genius"
            assert result.lyrics == "Is this the real life?\nIs this just fantasy?"
            assert result.synced_lyrics is None
            assert result.title == "Bohemian Rhapsody"
            assert result.artist == "Queen"

    def test_no_results(self, sample_metadata):
        """Return None when Genius returns no results."""
        with patch("lyricsgenius.Genius") as MockGenius:
            mock_genius = MagicMock()
            mock_genius.search_song.return_value = None
            MockGenius.return_value = mock_genius

            result = search_genius(sample_metadata, genius_token="test_token")
            assert result is None

    def test_lyricsgenius_import_error(self, sample_metadata):
        """Return None when lyricsgenius import fails."""
        with patch("builtins.__import__", side_effect=ImportError("No module named 'lyricsgenius'")):
            result = search_genius(sample_metadata, genius_token="test_token")
            assert result is None

    def test_genius_api_error(self, sample_metadata):
        """Return None when Genius API raises an error."""
        with patch("lyricsgenius.Genius") as MockGenius:
            MockGenius.side_effect = Exception("API Error")

            result = search_genius(sample_metadata, genius_token="test_token")
            assert result is None


class TestSearchLyrics:
    """Tests for search_lyrics function (orchestrator)."""

    def test_lrclib_priority(self, sample_metadata):
        """Return LRCLib result when available (priority over Genius)."""
        lrclib_result = LyricsResult(
            lyrics="LRCLib lyrics",
            synced_lyrics="[00:10.00]Synced",
            source="lrclib",
        )

        with patch("lrcgen.lyrics_search.search_lrclib") as mock_lrclib, \
             patch("lrcgen.lyrics_search.search_genius") as mock_genius:
            mock_lrclib.return_value = lrclib_result
            mock_genius.return_value = None

            result = search_lyrics(sample_metadata)

            assert result is not None
            assert result.source == "lrclib"
            mock_genius.assert_not_called()

    def test_genius_fallback(self, sample_metadata):
        """Fall back to Genius when LRCLib returns None."""
        genius_result = LyricsResult(
            lyrics="Genius lyrics",
            synced_lyrics=None,
            source="genius",
        )

        with patch("lrcgen.lyrics_search.search_lrclib") as mock_lrclib, \
             patch("lrcgen.lyrics_search.search_genius") as mock_genius:
            mock_lrclib.return_value = None
            mock_genius.return_value = genius_result

            result = search_lyrics(sample_metadata, genius_token="test_token")

            assert result is not None
            assert result.source == "genius"

    def test_no_results_anywhere(self, sample_metadata):
        """Return None when no source has lyrics."""
        with patch("lrcgen.lyrics_search.search_lrclib") as mock_lrclib, \
             patch("lrcgen.lyrics_search.search_genius") as mock_genius:
            mock_lrclib.return_value = None
            mock_genius.return_value = None

            result = search_lyrics(sample_metadata)
            assert result is None

    def test_passes_genius_token(self, sample_metadata):
        """Pass genius_token to search_genius."""
        with patch("lrcgen.lyrics_search.search_lrclib") as mock_lrclib, \
             patch("lrcgen.lyrics_search.search_genius") as mock_genius:
            mock_lrclib.return_value = None
            mock_genius.return_value = None

            search_lyrics(sample_metadata, genius_token="my_token")

            mock_genius.assert_called_once_with(sample_metadata, "my_token")
