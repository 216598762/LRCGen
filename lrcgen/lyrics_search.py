"""Search for lyrics from LRCLib and Genius APIs."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from lrcgen.metadata import AudioMetadata

logger = logging.getLogger(__name__)

LRCLIB_BASE_URL = "https://lrclib.net/api"


@dataclass
class LyricsResult:
    """Result from a lyrics search."""
    lyrics: str
    synced_lyrics: str | None  # LRC formatted if available
    source: str  # "lrclib" or "genius"
    title: str | None = None
    artist: str | None = None


def search_lrclib(metadata: AudioMetadata) -> LyricsResult | None:
    """Search LRCLib for synced lyrics.

    Args:
        metadata: Audio file metadata to search with.

    Returns:
        LyricsResult if found, None otherwise.
    """
    try:
        # Build search parameters
        params = {}
        if metadata.title:
            params["track_name"] = metadata.title
        if metadata.artist:
            params["artist_name"] = metadata.artist
        if metadata.album:
            params["album_name"] = metadata.album
        if metadata.duration:
            params["duration"] = str(int(metadata.duration))

        if not params:
            logger.warning("No metadata available for LRCLib search")
            return None

        logger.info(f"Searching LRCLib: {params}")
        response = requests.get(
            f"{LRCLIB_BASE_URL}/search",
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        results = response.json()

        if not results:
            logger.info("No results found on LRCLib")
            return None

        # Take the first result
        result = results[0]
        synced = result.get("syncedLyrics")
        plain = result.get("plainLyrics", "")

        if not synced and not plain:
            return None

        return LyricsResult(
            lyrics=plain,
            synced_lyrics=synced,
            source="lrclib",
            title=result.get("trackName"),
            artist=result.get("artistName"),
        )

    except requests.RequestException as e:
        logger.warning(f"LRCLib search failed: {e}")
        return None


def search_genius(metadata: AudioMetadata, genius_token: str | None = None) -> LyricsResult | None:
    """Search Genius for lyrics (plain text only).

    Note: Genius API requires an access token. The lyrics are scraped
    from the web page using the lyricsgenius library.

    Args:
        metadata: Audio file metadata to search with.
        genius_token: Genius API access token.

    Returns:
        LyricsResult if found, None otherwise.
    """
    if not genius_token:
        logger.warning("No Genius API token provided, skipping Genius search")
        return None

    try:
        import lyricsgenius

        genius = lyricsgenius.Genius(
            genius_token,
            verbose=False,
            remove_section_headers=True,
        )

        # Search using artist and title
        query = metadata.search_query
        logger.info(f"Searching Genius: {query}")

        song = genius.search_song(
            title=metadata.title or "",
            artist=metadata.artist or "",
        )

        if song is None:
            logger.info("No results found on Genius")
            return None

        return LyricsResult(
            lyrics=song.lyrics,
            synced_lyrics=None,  # Genius doesn't provide synced lyrics
            source="genius",
            title=song.title,
            artist=song.artist,
        )

    except ImportError:
        logger.warning("lyricsgenius not installed, skipping Genius search")
        return None
    except Exception as e:
        logger.warning(f"Genius search failed: {e}")
        return None


def search_lyrics(
    metadata: AudioMetadata,
    genius_token: str | None = None,
) -> LyricsResult | None:
    """Search for lyrics from all available sources.

    Priority: LRCLib (synced) > Genius (plain text)

    Args:
        metadata: Audio file metadata to search with.
        genius_token: Optional Genius API token for fallback.

    Returns:
        LyricsResult if found, None otherwise.
    """
    # Try LRCLib first (provides synced lyrics)
    result = search_lrclib(metadata)
    if result:
        logger.info(f"Found lyrics on LRCLib (synced: {result.synced_lyrics is not None})")
        return result

    # Fallback to Genius (plain text only)
    result = search_genius(metadata, genius_token)
    if result:
        logger.info("Found lyrics on Genius (plain text only)")
        return result

    logger.info("No lyrics found from any source")
    return None
