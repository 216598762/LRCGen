"""Extract metadata from audio files using mutagen."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mutagen import File


SUPPORTED_EXTENSIONS = {
    ".mp3", ".flac", ".ogg", ".opus", ".m4a", ".aac", ".wav",
    ".wma", ".aiff", ".ape", ".wv", ".mpc", ".tta", ".tak",
}


@dataclass
class AudioMetadata:
    """Metadata extracted from an audio file."""
    title: str | None
    artist: str | None
    album: str | None
    duration: float | None  # seconds
    file_path: Path

    @property
    def search_query(self) -> str:
        """Build a search query string from available metadata."""
        parts = []
        if self.artist:
            parts.append(self.artist)
        if self.title:
            parts.append(self.title)
        return " ".join(parts) if parts else self.file_path.stem

    @property
    def is_complete(self) -> bool:
        """Check if we have enough metadata to search for lyrics."""
        return self.title is not None and self.artist is not None


def extract_metadata(file_path: Path) -> AudioMetadata:
    """Extract metadata from an audio file.

    Args:
        file_path: Path to the audio file.

    Returns:
        AudioMetadata with extracted information.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the file type is not supported.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    suffix = file_path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported audio format: {suffix}. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    title = None
    artist = None
    album = None
    duration = None

    # Try easy=True first for simple tag access
    audio_easy = File(str(file_path), easy=True)
    if audio_easy is not None and audio_easy.tags:
        tags = audio_easy.tags
        title = _get_tag(tags, "title")
        artist = _get_tag(tags, "artist")
        album = _get_tag(tags, "album")

    # Get duration from audio info (works regardless of easy mode)
    audio_info = File(str(file_path))
    if audio_info is not None and hasattr(audio_info, "info") and hasattr(audio_info.info, "length"):
        duration = audio_info.info.length

    return AudioMetadata(
        title=title,
        artist=artist,
        album=album,
        duration=duration,
        file_path=file_path,
    )


def _get_tag(tags: dict, key: str) -> str | None:
    """Safely extract a tag value, handling list returns from easy=True."""
    value = tags.get(key)
    if value is None:
        return None
    if isinstance(value, list) and len(value) > 0:
        return str(value[0])
    return str(value)


def is_supported_audio(file_path: Path) -> bool:
    """Check if a file is a supported audio format."""
    return file_path.suffix.lower() in SUPPORTED_EXTENSIONS
