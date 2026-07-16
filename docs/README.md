# LRCGen Documentation

Welcome to the LRCGen documentation! This guide will help you get started with generating synchronized `.LRC` lyric files.

## Table of Contents

- [Getting Started](getting-started.md)
- [Installation](installation.md)
- [Usage Guide](usage.md)
- [Configuration](configuration.md)
- [API Reference](api-reference.md)
- [Contributing](../CONTRIBUTING.md)
- [Changelog](changelog.md)

## Quick Start

```bash
# Install LRCGen
pip install -e .

# Generate LRC for a single file
lrcgen song.mp3

# Generate LRC for entire directory
lrcgen /path/to/music/
```

## Features

- **Multi-source lyrics**: Fetches synced lyrics from LRCLib, with Genius as fallback
- **AI transcription**: Uses Faster-Whisper for accurate word-level timestamps
- **Smart matching**: Extracts metadata from audio files to find the right song
- **Wide format support**: MP3, FLAC, OGG, M4A, WAV, and many more
- **Batch processing**: Process entire directories recursively
- **Sidecar output**: LRC files created next to audio files automatically
