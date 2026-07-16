# Getting Started

This guide will help you get up and running with LRCGen quickly.

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git

## Installation

### From Source (Recommended)

```bash
# Clone the repository
git clone https://github.com/216598762/LRCGen.git
cd LRCGen

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Verify Installation

```bash
# Check version
lrcgen --help

# Run tests
pytest tests/ -v
```

## Your First LRC File

1. **Find an audio file** with metadata (title, artist tags)

2. **Run LRCGen**:
   ```bash
   lrcgen song.mp3
   ```

3. **Check the output** - a `song.lrc` file will be created next to your audio file

## How It Works

LRCGen follows this process:

1. **Metadata Extraction**: Reads artist, title, and album from audio file tags
2. **Lyrics Search**: Queries LRCLib for synced lyrics, falls back to Genius
3. **AI Transcription**: If needed, uses Faster-Whisper for word-level timestamps
4. **LRC Generation**: Creates properly formatted `.LRC` files with metadata tags

## Next Steps

- Read the [Usage Guide](usage.md) for all available options
- Check [Configuration](configuration.md) for advanced settings
- See [API Reference](api-reference.md) for the Python API
