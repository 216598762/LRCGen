# Installation

## Requirements

- Python 3.10 or higher
- pip (Python package manager)

## Install from Source

### Option 1: Development Mode (Recommended)

```bash
git clone https://github.com/216598762/LRCGen.git
cd LRCGen
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Option 2: Regular Install

```bash
git clone https://github.com/216598762/LRCGen.git
cd LRCGen
pip install .
```

## Dependencies

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| mutagen | >=1.47.0 | Audio metadata extraction |
| requests | >=2.31.0 | HTTP requests for lyrics APIs |
| faster-whisper | >=1.0.0 | AI transcription |
| lyricsgenius | >=1.4.0 | Genius API integration |
| rich | >=13.0.0 | Beautiful terminal output |
| click | >=8.1.0 | CLI framework |

### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pytest | >=7.0 | Testing framework |
| pytest-cov | - | Code coverage |
| ruff | - | Linting and formatting |
| mypy | - | Static type checking |
| pre-commit | - | Git hooks |

## Optional: Genius API Token

To use Genius as a fallback for lyrics, you'll need an API token:

1. Create a Genius account at https://genius.com
2. Go to https://genius.com/api-clients
3. Create a new API client
4. Generate an Access Token
5. Set the environment variable:
   ```bash
   export GENIUS_ACCESS_TOKEN="your_token_here"
   ```

## Verify Installation

```bash
# Check if lrcgen is installed
lrcgen --help

# Run the test suite
pytest tests/ -v
```

## Troubleshooting

### Common Issues

**ModuleNotFoundError: No module named 'faster_whisper'**
```bash
pip install faster-whisper
```

**ImportError: cannot import name 'LyricsResult'**
```bash
pip install -e ".[dev]"
```

**Permission denied**
```bash
# Use --user flag or virtual environment
pip install --user -e .
```

### Getting Help

If you encounter issues not covered here:
1. Check the [GitHub Issues](https://github.com/216598762/LRCGen/issues)
2. Search existing issues for solutions
3. Open a new issue with details about your problem
