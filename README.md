# LRCGen

Generate synchronized `.LRC` lyric files for your audio collection using AI-powered transcription and online lyrics databases.

## Features

- **Multi-source lyrics**: Fetches synced lyrics from LRCLib, with Genius as fallback
- **AI transcription**: Uses Faster-Whisper for accurate word-level timestamps
- **Smart matching**: Extracts metadata from audio files to find the right song
- **Wide format support**: MP3, FLAC, OGG, M4A, WAV, and many more
- **Batch processing**: Process entire directories recursively
- **Sidecar output**: LRC files created next to audio files automatically
- **Time offset**: Adjust all timestamps by a global offset
- **Flexible filtering**: Include/exclude files with glob patterns
- **Dry run mode**: Preview what would be done without processing

## Installation

```bash
# Install from source
pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# Process a single file
lrcgen song.mp3

# Process a directory recursively
lrcgen /path/to/music/

# Process current directory (non-recursive)
lrcgen . --no-recursive
```

### All Options

```
Usage: lrcgen [OPTIONS] PATH

  LRCGen - Generate synchronized .LRC lyric files.

  PATH can be a single audio file or a directory to scan.

  Examples:
    lrcgen song.mp3
    lrcgen /path/to/music/ --model-size medium --device cuda
    lrcgen music/ --dry-run --verbose
    lrcgen music/ --skip-whisper --genius-only

Options:
  -o, --output-dir PATH            Output directory for LRC files.
  -m, --model-size TEXT            Whisper model size (tiny, base, small, medium,
                                   large-v3).  [default: small]
  -d, --device TEXT                Device for Whisper (cpu, cuda, auto).
                                   [default: cpu]
  --genius-token TEXT              Genius API token (or set GENIUS_ACCESS_TOKEN
                                   env var).
  -r, --recursive/--no-recursive   Recursively scan directories.
                                   [default: recursive]
  -f, --force                      Force regeneration of existing LRC files.
  -l, --language TEXT              Language code for Whisper (e.g., en, es, ja).
                                   Auto-detect if not set.
  -v, --verbose                    Enable verbose debug logging.
  -q, --quiet                      Suppress output except errors.
  --dry-run                        Preview what would be done without processing
                                   files.
  --skip-whisper                   Skip Whisper transcription (only use online
                                   lyrics).
  --skip-lyrics                    Skip lyrics search (only use Whisper
                                   transcription).
  --lrclib-only                    Only search LRCLib (skip Genius fallback).
  --genius-only                    Only search Genius (skip LRCLib).
  --offset INTEGER                 Global time offset in milliseconds (positive
                                   delays, negative advances).  [default: 0]
  --no-metadata                    Don't include metadata tags (title, artist,
                                   album) in LRC.
  --beam-size INTEGER              Whisper beam size for transcription.
                                   [default: 5]
  --compute-type [int8|float16|float32]
                                   Whisper compute type (int8=fast, float16=gpu,
                                   float32=best quality).  [default: int8]
  --extensions TEXT                 Comma-separated audio extensions to include
                                   (default: all supported).
  --exclude TEXT                   Glob patterns to exclude (can be specified
                                   multiple times).
  --include TEXT                   Glob patterns to include (can be specified
                                   multiple times).
  --version                        Show version and exit.
  --no-color                       Disable colored output.
  --help                           Show this message and exit.
```

### Examples

#### Basic Processing

```bash
# Process a single file
lrcgen song.mp3

# Process a directory
lrcgen /path/to/music/

# Process current directory non-recursively
lrcgen . --no-recursive
```

#### Whisper Configuration

```bash
# Use a larger model for better accuracy
lrcgen music/ --model-size medium

# Use GPU acceleration with float16
lrcgen music/ --device cuda --compute-type float16

# Use best quality (slower)
lrcgen music/ --compute-type float32

# Set beam size for better accuracy
lrcgen music/ --beam-size 10

# Specify language for better recognition
lrcgen music/ --language ja
```

#### Lyrics Source Control

```bash
# Only use LRCLib (skip Genius)
lrcgen music/ --lrclib-only

# Only use Genius (skip LRCLib)
lrcgen music/ --genius-only --genius-token YOUR_TOKEN

# Skip Whisper, only use online lyrics
lrcgen music/ --skip-whisper

# Skip lyrics search, only use Whisper transcription
lrcgen music/ --skip-lyrics
```

#### Output Control

```bash
# Output to a specific directory
lrcgen music/ -o lrc_output/

# Force regenerate all LRC files
lrcgen music/ --force

# Apply time offset (delay all lyrics by 500ms)
lrcgen music/ --offset 500

# Apply negative offset (advance all lyrics by 200ms)
lrcgen music/ --offset -200

# Create LRC without metadata tags
lrcgen music/ --no-metadata
```

#### File Filtering

```bash
# Only process MP3 and FLAC files
lrcgen music/ --extensions ".mp3,.flac"

# Exclude live recordings
lrcgen music/ --exclude "*live*"

# Include only files matching a pattern
lrcgen music/ --include "*.mp3" --include "*album*"

# Multiple exclude patterns
lrcgen music/ --exclude "*.temp.*" --exclude "*test*"
```

#### Preview and Debugging

```bash
# Dry run - see what would be processed
lrcgen music/ --dry-run

# Verbose output
lrcgen music/ --verbose

# Quiet mode (only errors)
lrcgen music/ --quiet

# Disable colors
lrcgen music/ --no-color

# Show version
lrcgen --version
```

#### Environment Variables

```bash
# Set Genius token via environment variable
export GENIUS_ACCESS_TOKEN=your_token_here
lrcgen music/
```

## How It Works

1. **Metadata Extraction**: Reads artist, title, and album from audio file tags
2. **Lyrics Search**: Queries LRCLib for synced lyrics, falls back to Genius
3. **AI Transcription**: If needed, uses Faster-Whisper for word-level timestamps
4. **LRC Generation**: Creates properly formatted `.LRC` files with metadata tags

## LRC File Format

```lrc
[ti:Song Title]
[ar:Artist Name]
[al:Album Name]
[length:03:45]
[by:LRCGen]
[00:12.00]First line of lyrics
[00:15.30]Second line of lyrics
[00:18.50]Third line of lyrics
```

## Configuration

### Environment Variables

- `GENIUS_ACCESS_TOKEN`: Your Genius API access token (optional, for fallback lyrics)

### Whisper Models

| Model    | Size    | Speed   | Accuracy |
|----------|---------|---------|----------|
| tiny     | ~39MB   | Fastest | Basic    |
| base     | ~74MB   | Fast    | Good     |
| small    | ~244MB  | Medium  | Better   |
| medium   | ~769MB  | Slow    | Great    |
| large-v3 | ~1550MB | Slowest | Best     |

### Compute Types

| Type    | Speed   | Quality | Use Case |
|---------|---------|---------|----------|
| int8    | Fastest | Good    | CPU, balanced |
| float16 | Fast    | Great   | GPU |
| float32 | Slow    | Best    | High quality |

## Supported Audio Formats

MP3, FLAC, OGG, Opus, M4A, AAC, WAV, WMA, AIFF, APE, WavPack, Musepack, True Audio

## License

MIT
