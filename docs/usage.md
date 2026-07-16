# Usage Guide

## Basic Usage

### Process a Single File

```bash
lrcgen song.mp3
```

This creates `song.lrc` next to `song.mp3`.

### Process a Directory

```bash
lrcgen /path/to/music/
```

Recursively scans for audio files and creates LRC files.

### Process Current Directory

```bash
lrcgen .
```

## Command Options

### Output Directory

```bash
lrcgen music/ -o lrc_output/
```

Writes all LRC files to the specified directory.

### Whisper Model Size

```bash
lrcgen music/ --model-size tiny    # Fastest, least accurate
lrcgen music/ --model-size base    # Fast
lrcgen music/ --model-size small   # Balanced (default)
lrcgen music/ --model-size medium  # More accurate
lrcgen music/ --model-size large-v3 # Most accurate, slowest
```

### GPU Acceleration

```bash
lrcgen music/ --device cuda
```

### Force Regeneration

```bash
lrcgen music/ --force
```

Overwrites existing LRC files.

### Specify Language

```bash
lrcgen music/ --language en    # English
lrcgen music/ --language es    # Spanish
lrcgen music/ --language ja    # Japanese
```

### Non-Recursive Scanning

```bash
lrcgen music/ --no-recursive
```

Only processes files in the root directory.

### Verbose Output

```bash
lrcgen music/ --verbose
```

Shows detailed logging information.

## Examples

### Example 1: Basic Processing

```bash
$ lrcgen ~/Music/album/
Scanning: /home/user/Music/album/
Found: 12 audio file(s)

Processing: track01.mp3
  Metadata: Queen - Bohemian Rhapsody
  Found synced lyrics from LRCLib
  ✓ Created: track01.lrc

Processing: track02.flac
  Metadata: Queen - Somebody to Love
  Using Whisper for transcription...
  ✓ Created: track02.lrc

Summary: 12 succeeded, 0 failed
```

### Example 2: Custom Output Directory

```bash
$ lrcgen ~/Music/album/ -o ~/Lyrics/
Scanning: /home/user/Music/album/
Found: 12 audio file(s)
...
Summary: 12 succeeded, 0 failed
```

### Example 3: Force Regenerate

```bash
$ lrcgen ~/Music/album/ --force
Scanning: /home/user/Music/album/
Found: 12 audio file(s)

Processing: track01.mp3
  Metadata: Queen - Bohemian Rhapsody
  Found synced lyrics from LRCLib
  ✓ Created: track01.lrc
...
```

## Supported Audio Formats

LRCGen supports the following audio formats:

| Format | Extension |
|--------|-----------|
| MP3 | .mp3 |
| FLAC | .flac |
| OGG | .ogg |
| Opus | .opus |
| M4A | .m4a |
| AAC | .aac |
| WAV | .wav |
| WMA | .wma |
| AIFF | .aiff |
| APE | .ape |
| WavPack | .wv |
| Musepack | .mpc |
| True Audio | .tta |
| TAK | .tak |

## LRC File Format

LRC files follow this format:

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

### Metadata Tags

| Tag | Description |
|-----|-------------|
| `[ti:]` | Song title |
| `[ar:]` | Artist name |
| `[al:]` | Album name |
| `[length:]` | Song length (mm:ss) |
| `[by:]` | LRC file creator |

### Timestamps

Timestamps follow the format `[mm:ss.xx]`:
- `mm` - Minutes (00-99)
- `ss` - Seconds (00-59)
- `xx` - Hundredths of a second (00-99)
