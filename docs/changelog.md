# Changelog

All notable changes to LRCGen will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of LRCGen
- LRCLib integration for synced lyrics
- Genius API fallback for plain text lyrics
- Faster-Whisper integration for AI transcription
- Support for 14+ audio formats
- Recursive directory scanning
- Sidecar LRC file output
- Configurable Whisper model size
- GPU acceleration support
- Rich terminal output with progress bars

### Changed
- Renamed `_format_lrc_timestamp` to `format_lrc_timestamp` (public API)

### Fixed
- Empty segments guard when Whisper returns no audio
- Metadata extraction fallback for non-easy mutagen formats

## [0.1.0] - 2026-07-16

### Added
- Core functionality for LRC generation
- Metadata extraction using mutagen
- Lyrics search from LRCLib and Genius
- Whisper transcription with word-level timestamps
- CLI interface with Click
- Comprehensive test suite (108 tests)
- Pre-commit hooks for ruff and mypy
- GitHub Actions CI/CD pipeline
- Documentation

### Technical Details
- Python 3.10+ required
- Dependencies: mutagen, requests, faster-whisper, lyricsgenius, rich, click
- Dev dependencies: pytest, ruff, mypy, pre-commit

---

For a complete list of changes, see the [GitHub Releases](https://github.com/216598762/LRCGen/releases).
