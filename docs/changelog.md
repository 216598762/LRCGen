# Changelog

All notable changes to LRCGen will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-16

### Added
- LRCLib integration for synced lyrics
- Genius API fallback for plain text lyrics
- Faster-Whisper integration for AI transcription with word-level timestamps
- Support for 14+ audio formats (MP3, FLAC, OGG, M4A, WAV, and more)
- Recursive directory scanning
- Sidecar LRC file output (creates LRC next to audio files)
- Configurable Whisper model size (tiny/base/small/medium/large-v3)
- GPU acceleration support via CUDA
- Rich terminal output with progress bars
- Metadata extraction using mutagen
- CLI interface with Click
- Comprehensive test suite (108 tests)
- Pre-commit hooks for ruff and mypy
- GitHub Actions CI/CD pipeline
- Documentation

### Changed
- Public API: `format_lrc_timestamp` (was `_format_lrc_timestamp`)

### Fixed
- Empty segments guard when Whisper returns no audio
- Metadata extraction fallback for non-easy mutagen formats

### Technical Details
- Python 3.10+ required
- Dependencies: mutagen, requests, faster-whisper, lyricsgenius, rich, click
- Dev dependencies: pytest, ruff, mypy, pre-commit

---

For a complete list of changes, see the [GitHub Releases](https://github.com/216598762/LRCGen/releases).
