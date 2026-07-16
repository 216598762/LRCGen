# Changelog

All notable changes to LRCGen will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-16

### Added
- Extensive CLI arguments for fine-grained control:
  - `--version`: Show version and exit
  - `--dry-run`: Preview what would be done without processing files
  - `--skip-whisper`: Skip Whisper transcription (use online lyrics only)
  - `--skip-lyrics`: Skip lyrics search (use Whisper only)
  - `--lrclib-only`: Only search LRCLib (skip Genius)
  - `--genius-only`: Only search Genius (skip LRCLib)
  - `--offset`: Global time offset in milliseconds for all LRC timestamps
  - `--no-metadata`: Don't include metadata tags in LRC files
  - `--beam-size`: Configurable Whisper beam size for transcription
  - `--compute-type`: Whisper compute type selection (int8/float16/float32)
  - `--extensions`: Filter audio files by extensions
  - `--exclude`: Glob patterns to exclude files (repeatable)
  - `--include`: Glob patterns to include files (repeatable)
  - `--quiet`: Suppress output except errors
  - `--no-color`: Disable colored terminal output
- Proper glob pattern matching using `fnmatch` for include/exclude
- Updated whisper_sync.py to accept beam_size and compute_type parameters
- Comprehensive README documentation for all CLI options

### Changed
- CLI argument handling restructured for better extensibility
- Version flag now uses Click's built-in `version_option` decorator

### Fixed
- Include/exclude pattern matching now uses proper glob syntax

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
