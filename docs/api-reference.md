# API Reference

LRCGen provides a Python API for programmatic use.

## Core Modules

### lrcgen.metadata

Extract metadata from audio files.

#### AudioMetadata

```python
@dataclass
class AudioMetadata:
    title: str | None
    artist: str | None
    album: str | None
    duration: float | None  # seconds
    file_path: Path

    @property
    def search_query(self) -> str:
        """Build a search query string from available metadata."""

    @property
    def is_complete(self) -> bool:
        """Check if we have enough metadata to search for lyrics."""
```

#### extract_metadata

```python
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
```

#### is_supported_audio

```python
def is_supported_audio(file_path: Path) -> bool:
    """Check if a file is a supported audio format."""
```

### lrcgen.lyrics_search

Search for lyrics from online sources.

#### LyricsResult

```python
@dataclass
class LyricsResult:
    lyrics: str
    synced_lyrics: str | None  # LRC formatted if available
    source: str  # "lrclib" or "genius"
    title: str | None = None
    artist: str | None = None
```

#### search_lyrics

```python
def search_lyrics(
    metadata: AudioMetadata,
    genius_token: str | None = None,
) -> LyricsResult | None:
    """Search for lyrics from all available sources.

    Priority: LRCLib (synced) > Genius (plain text)
    """
```

#### search_lrclib

```python
def search_lrclib(metadata: AudioMetadata) -> LyricsResult | None:
    """Search LRCLib for synced lyrics."""
```

#### search_genius

```python
def search_genius(
    metadata: AudioMetadata,
    genius_token: str | None = None,
) -> LyricsResult | None:
    """Search Genius for lyrics (plain text only)."""
```

### lrcgen.whisper_sync

Transcribe audio using Faster-Whisper.

#### Segment

```python
@dataclass
class Segment:
    text: str
    start: float  # seconds
    end: float    # seconds
    words: list[WordTimestamp]
```

#### WordTimestamp

```python
@dataclass
class WordTimestamp:
    word: str
    start: float  # seconds
    end: float    # seconds
```

#### transcribe_audio

```python
def transcribe_audio(
    audio_path: Path,
    model_size: str = "small",
    device: str = "cpu",
    language: str | None = None,
) -> list[Segment]:
    """Transcribe audio file with word-level timestamps."""
```

### lrcgen.lrc_writer

Generate LRC files.

#### create_lrc_from_synced

```python
def create_lrc_from_synced(
    synced_lrc: str,
    title: str | None = None,
    artist: str | None = None,
    album: str | None = None,
    duration: float | None = None,
) -> str:
    """Create an LRC file from synced LRC text (from LRCLib)."""
```

#### create_lrc_from_lines

```python
def create_lrc_from_lines(
    timestamped_lines: list[tuple[str, str]],
    title: str | None = None,
    artist: str | None = None,
    album: str | None = None,
    duration: float | None = None,
) -> str:
    """Create an LRC file from timestamped lines."""
```

#### create_lrc_from_plain_text

```python
def create_lrc_from_plain_text(
    plain_lyrics: str,
    timestamps: list[tuple[float, float]],
    title: str | None = None,
    artist: str | None = None,
    album: str | None = None,
    duration: float | None = None,
) -> str:
    """Create an LRC file from plain text lyrics and Whisper timestamps."""
```

#### format_lrc_timestamp

```python
def format_lrc_timestamp(seconds: float) -> str:
    """Format seconds to LRC timestamp [mm:ss.xx]."""
```

#### write_lrc_file

```python
def write_lrc_file(content: str, output_path: Path) -> Path:
    """Write LRC content to a file."""
```

### lrcgen.cli

Command-line interface functions.

#### process_audio_file

```python
def process_audio_file(
    audio_path: Path,
    model_size: str,
    device: str,
    genius_token: str | None,
    output_dir: Path | None,
    force: bool,
    language: str | None,
) -> bool:
    """Process a single audio file.

    Returns:
        True if successful, False otherwise.
    """
```

#### find_audio_files

```python
def find_audio_files(path: Path, recursive: bool = True) -> list[Path]:
    """Find all supported audio files in a directory."""
```

## Usage Examples

### Example 1: Extract Metadata

```python
from lrcgen.metadata import extract_metadata

metadata = extract_metadata(Path("song.mp3"))
print(f"Title: {metadata.title}")
print(f"Artist: {metadata.artist}")
print(f"Duration: {metadata.duration:.1f}s")
```

### Example 2: Search for Lyrics

```python
from lrcgen.metadata import extract_metadata
from lrcgen.lyrics_search import search_lyrics

metadata = extract_metadata(Path("song.mp3"))
result = search_lyrics(metadata, genius_token="your_token")

if result:
    print(f"Found lyrics from {result.source}")
    if result.synced_lyrics:
        print("Has synced lyrics!")
```

### Example 3: Generate LRC

```python
from lrcgen.lrc_writer import create_lrc_from_synced, write_lrc_file

synced = "[00:10.00]Hello world\n[00:15.00]Goodbye world"
lrc_content = create_lrc_from_synced(
    synced,
    title="My Song",
    artist="My Artist",
)

write_lrc_file(lrc_content, Path("song.lrc"))
```

### Example 4: Full Pipeline

```python
from pathlib import Path
from lrcgen.metadata import extract_metadata
from lrcgen.lyrics_search import search_lyrics
from lrcgen.whisper_sync import transcribe_audio
from lrcgen.lrc_writer import (
    create_lrc_from_synced,
    create_lrc_from_plain_text,
    write_lrc_file,
)

def process_song(audio_path: Path):
    # Extract metadata
    metadata = extract_metadata(audio_path)

    # Search for lyrics
    result = search_lyrics(metadata)

    if result and result.synced_lyrics:
        # Use synced lyrics directly
        lrc = create_lrc_from_synced(result.synced_lyrics, ...)
    else:
        # Use Whisper for timestamps
        segments = transcribe_audio(audio_path)
        # ... create LRC from segments

    # Write output
    write_lrc_file(lrc, audio_path.with_suffix(".lrc"))
```
