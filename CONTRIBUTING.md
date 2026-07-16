# Contributing to LRCGen

Thank you for your interest in contributing to LRCGen! This document provides guidelines and information for contributors.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Reporting Issues](#reporting-issues)
- [Code of Conduct](#code-of-conduct)

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/LRCGen.git
   cd LRCGen
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/216598762/LRCGen.git
   ```
4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git

### Installation

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install the package in development mode**:
   ```bash
   pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

### Optional: Genius API Token

If you want to test Genius API integration:
```bash
export GENIUS_ACCESS_TOKEN="your_token_here"
```

## Code Style

We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting.

### Formatting

```bash
# Check formatting
ruff format --check .

# Auto-format
ruff format .
```

### Linting

```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check --fix .
```

### Type Checking

```bash
# Run mypy
mypy lrcgen/ --ignore-missing-imports
```

### Pre-commit Hooks

Pre-commit hooks run automatically on `git commit`. They check:
- Code formatting (ruff)
- Linting (ruff)
- Type checking (mypy)

To run manually:
```bash
pre-commit run --all-files
```

### Code Conventions

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guide
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions focused and under 50 lines when possible
- Use meaningful variable and function names

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=lrcgen --cov-report=term-missing

# Run specific test file
pytest tests/test_metadata.py -v

# Run specific test
pytest tests/test_metadata.py::TestExtractMetadata::test_extract_from_mp3 -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use fixtures for common test data
- Mock external dependencies (APIs, file system)

Example test:
```python
import pytest
from lrcgen.metadata import AudioMetadata

def test_search_query():
    """Test that search query builds correctly."""
    meta = AudioMetadata(
        title="Test Song",
        artist="Test Artist",
        album=None,
        duration=None,
        file_path=Path("/fake.mp3"),
    )
    assert meta.search_query == "Test Artist Test Song"
```

### Test Coverage

We aim for at least 80% test coverage. Check coverage with:
```bash
pytest tests/ --cov=lrcgen --cov-report=html
open htmlcov/index.html  # View report
```

## Pull Request Process

### Before Submitting

1. **Update your fork**:
   ```bash
   git fetch upstream
   git rebase upstream/master
   ```

2. **Run tests**:
   ```bash
   pytest tests/ -v
   ```

3. **Run linter**:
   ```bash
   ruff check .
   ruff format --check .
   ```

4. **Run type checker**:
   ```bash
   mypy lrcgen/ --ignore-missing-imports
   ```

5. **Commit your changes** (see [Commit Message Guidelines](#commit-message-guidelines))

### Submitting a Pull Request

1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request** on GitHub

3. **Fill out the PR template**:
   - Description of changes
   - Related issues (if any)
   - Testing done
   - Checklist (tests pass, linting passes, etc.)

### PR Requirements

- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Type checking passes
- [ ] Documentation is updated (if applicable)
- [ ] Commit messages follow guidelines
- [ ] PR has a clear description

## Commit Message Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks
- **perf**: Performance improvements

### Examples

```
feat(lyrics): add Genius API fallback support
fix(metadata): handle missing title tag gracefully
docs(readme): update installation instructions
test(cli): add integration tests for batch processing
chore(deps): update faster-whisper to 1.0.1
```

### Scope

Optional scope that provides contextual information:

- `metadata` - Audio metadata extraction
- `lyrics` - Lyrics fetching (LRCLib, Genius)
- `whisper` - Whisper transcription
- `cli` - Command line interface
- `lrc` - LRC file generation
- `deps` - Dependencies

## Reporting Issues

### Bug Reports

When filing a bug report, please include:

1. **Environment information**:
   - Python version (`python --version`)
   - OS and version
   - Package version

2. **Steps to reproduce**:
   - Exact commands run
   - Input files (if applicable)
   - Expected behavior
   - Actual behavior

3. **Error messages**:
   - Full traceback
   - Log output (if available)

### Feature Requests

When requesting a feature, please include:

1. **Problem description**: What problem does this solve?
2. **Proposed solution**: How should it work?
3. **Alternatives considered**: Other approaches
4. **Additional context**: Examples, mockups, etc.

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive experience for everyone.

### Expected Behavior

- Be respectful and inclusive
- Accept constructive criticism
- Focus on what is best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment, trolling, or discrimination
- Publishing others' private information
- Other conduct deemed inappropriate

## Questions?

If you have questions about contributing, feel free to:

1. Open a [discussion](https://github.com/216598762/LRCGen/discussions)
2. Comment on an existing issue
3. Reach out to maintainers

Thank you for contributing to LRCGen! 🎵
