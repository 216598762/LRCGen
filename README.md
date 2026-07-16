# LRCGen

Generate synchronized `.LRC` lyric files for your audio collection using AI-powered transcription and online lyrics databases.

## Features

- **Multi-source lyrics**: Fetches synced lyrics from LRCLib, with Genius as fallback
- **AI transcription**: Uses Faster-Whisper for accurate word-level timestamps
- **Smart matching**: Extracts metadata from audio files to find the right song
- **Wide format support**: MP3, FLAC, OGG, M4A, WAV, and many more
- **Batch processing**: Process entire directories recursively
- **Sidecar output**: LRC files created next to audio files automatically

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

### Options

```bash
lrcgen --help

Options:
  -o, --output-dir PATH     Output directory for LRC files
  -m, --model-size TEXT     Whisper model size (tiny/base/small/medium/large-v3)
                             [default: small]
  -d, --device TEXT         Device for Whisper (cpu/cuda) [default: cpu]
  --genius-token TEXT       Genius API token (or set GENIUS_ACCESS_TOKEN env var)
  -r, --recursive/--no-recursive
                             Recursively scan directories [default: recursive]
  -f, --force               Force regeneration of existing LRC files
  -l, --language TEXT       Language code for Whisper (e.g., en, es)
  -v, --verbose             Enable verbose logging
```

### Examples

```bash
# Use a larger model for better accuracy
lrcgen music/ --model-size medium

# Use GPU acceleration
lrcgen music/ --device cuda

# Force regenerate all LRC files
lrcgen music/ --force

# Output to a specific directory
lrcgen music/ -o lrc_output/

# With Genius API token for fallback lyrics
lrcgen music/ --genius-token YOUR_TOKEN
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

| Model   | Size    | Speed   | Accuracy |
|---------|---------|---------|----------|
| tiny    | ~39MB   | Fastest | Basic    |
| base    | ~74MB   | Fast    | Good     |
| small   | ~244MB  | Medium  | Better   |
| medium  | ~769MB  | Slow    | Great    |
| large-v3| ~1550MB | Slowest | Best     |

## Supported Audio Formats

MP3, FLAC, OGG, Opus, M4A, AAC, WAV, WMA, AIFF, APE, WavPack, Musepack, True Audio

## License

MIT
