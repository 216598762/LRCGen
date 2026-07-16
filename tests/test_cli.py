"""Tests for lrcgen.cli module using Click's CliRunner."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from lrcgen.cli import find_audio_files, main


@pytest.fixture
def runner():
    """Create a Click CliRunner instance."""
    return CliRunner()


class TestFindAudioFiles:
    """Tests for find_audio_files helper function."""

    def test_single_audio_file(self, create_minimal_mp3):
        """Return single file when given an audio file path."""
        filepath = create_minimal_mp3("song.mp3")
        result = find_audio_files(filepath)
        assert result == [filepath]

    def test_non_audio_file(self, create_minimal_mp3):
        """Return empty list for non-audio file."""
        # Create a text file in the same temp directory
        mp3_path = create_minimal_mp3("dummy.mp3")
        text_file = mp3_path.parent / "notes.txt"
        text_file.write_text("not audio")
        result = find_audio_files(text_file)
        assert result == []

    def test_directory_recursive(self, create_minimal_mp3):
        """Find audio files recursively in subdirectories."""
        filepath = create_minimal_mp3("root_song.mp3")
        base_dir = filepath.parent

        # Create subdirectory with another audio file
        subdir = base_dir / "subdir"
        subdir.mkdir()
        nested = subdir / "nested_song.mp3"
        nested.write_bytes(b"\xff\xfb\x90\x00" + b"\x00" * 413)

        result = find_audio_files(base_dir, recursive=True)
        assert len(result) == 2
        names = [p.name for p in result]
        assert "root_song.mp3" in names
        assert "nested_song.mp3" in names

    def test_directory_non_recursive(self, create_minimal_mp3):
        """Find audio files only in root directory when non-recursive."""
        filepath = create_minimal_mp3("root_song.mp3")
        base_dir = filepath.parent

        # Create subdirectory with another audio file
        subdir = base_dir / "subdir"
        subdir.mkdir()
        nested = subdir / "nested_song.mp3"
        nested.write_bytes(b"\xff\xfb\x90\x00" + b"\x00" * 413)

        result = find_audio_files(base_dir, recursive=False)
        assert len(result) == 1
        assert "root_song.mp3" in result[0].name

    def test_empty_directory(self, create_minimal_mp3):
        """Return empty list for directory with no audio files."""
        filepath = create_minimal_mp3("dummy.mp3")
        empty_dir = filepath.parent / "empty_subdir"
        empty_dir.mkdir()
        result = find_audio_files(empty_dir)
        assert result == []

    def test_sorted_output(self, create_minimal_mp3):
        """Results are sorted alphabetically."""
        create_minimal_mp3("zebra.mp3")
        create_minimal_mp3("apple.mp3")
        filepath = create_minimal_mp3("mango.mp3")
        base_dir = filepath.parent

        result = find_audio_files(base_dir)
        names = [p.name for p in result]
        assert names == sorted(names)

    def test_extensions_filter(self, create_minimal_mp3):
        """Filter audio files by extension."""
        mp3_file = create_minimal_mp3("song.mp3")
        base_dir = mp3_file.parent

        # Create FLAC file
        flac_file = base_dir / "track.flac"
        flac_file.write_bytes(b"\x66\x4c\x61\x43\x00\x00\x00\x22" + b"\x00" * 34)

        # Create OGG file
        ogg_file = base_dir / "audio.ogg"
        ogg_file.write_bytes(b"\x4f\x67\x67\x53\x00\x02\x00\x00" + b"\x00" * 8)

        # Filter only MP3
        result = find_audio_files(base_dir, extensions=".mp3")
        assert len(result) == 1
        assert result[0].name == "song.mp3"

        # Filter MP3 and FLAC
        result = find_audio_files(base_dir, extensions=".mp3,.flac")
        assert len(result) == 2
        names = [p.name for p in result]
        assert "song.mp3" in names
        assert "track.flac" in names

    def test_exclude_patterns(self, create_minimal_mp3):
        """Exclude files matching patterns."""
        create_minimal_mp3("normal.mp3")
        create_minimal_mp3("live_concert.mp3")
        create_minimal_mp3("remix_v2.mp3")
        filepath = create_minimal_mp3("test.mp3")
        base_dir = filepath.parent

        result = find_audio_files(base_dir, exclude_patterns=["*live*"])
        assert len(result) == 3
        names = [p.name for p in result]
        assert "live_concert.mp3" not in names

    def test_include_patterns(self, create_minimal_mp3):
        """Include only files matching patterns."""
        create_minimal_mp3("song.mp3")
        create_minimal_mp3("album_track.mp3")
        filepath = create_minimal_mp3("demo.mp3")
        base_dir = filepath.parent

        result = find_audio_files(base_dir, include_patterns=["*album*"])
        assert len(result) == 1
        assert result[0].name == "album_track.mp3"


class TestMainCommand:
    """Tests for the main CLI command."""

    def test_help_message(self, runner):
        """Show help message with --help flag."""
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "LRCGen" in result.output
        assert "PATH" in result.output

    def test_missing_path_argument(self, runner):
        """Error when no path argument provided."""
        result = runner.invoke(main, [])
        assert result.exit_code != 0

    def test_nonexistent_path(self, runner):
        """Error when path does not exist."""
        result = runner.invoke(main, ["/nonexistent/path"])
        assert result.exit_code != 0

    def test_empty_directory(self, runner, create_minimal_mp3):
        """Exit with error code when no audio files found."""
        filepath = create_minimal_mp3("dummy.mp3")
        empty_dir = filepath.parent / "empty_subdir"
        empty_dir.mkdir()
        result = runner.invoke(main, [str(empty_dir)])
        assert result.exit_code == 1
        assert "No supported audio files found" in result.output

    def test_with_audio_files(self, runner, create_minimal_mp3):
        """Process audio files in a directory."""
        filepath = create_minimal_mp3("test_song.mp3")
        result = runner.invoke(main, [str(filepath.parent)])
        # Should find the file and attempt processing
        assert "Found:" in result.output
        assert "1 audio file" in result.output

    def test_recursive_flag(self, runner, create_minimal_mp3):
        """Recursive flag works correctly."""
        filepath = create_minimal_mp3("root.mp3")
        base_dir = filepath.parent

        subdir = base_dir / "sub"
        subdir.mkdir()
        (subdir / "nested.mp3").write_bytes(b"\xff\xfb\x90\x00" + b"\x00" * 413)

        result = runner.invoke(main, [str(base_dir), "--recursive"])
        assert "Found:" in result.output
        assert "2 audio file" in result.output

    def test_no_recursive_flag(self, runner, create_minimal_mp3):
        """No-recursive flag skips subdirectories."""
        filepath = create_minimal_mp3("root.mp3")
        base_dir = filepath.parent

        subdir = base_dir / "sub"
        subdir.mkdir()
        (subdir / "nested.mp3").write_bytes(b"\xff\xfb\x90\x00" + b"\x00" * 413)

        result = runner.invoke(main, [str(base_dir), "--no-recursive"])
        assert "Found:" in result.output
        assert "1 audio file" in result.output

    def test_verbose_flag(self, runner, create_minimal_mp3):
        """Verbose flag is accepted."""
        filepath = create_minimal_mp3("test.mp3")
        result = runner.invoke(main, [str(filepath.parent), "--verbose"])
        assert "Found:" in result.output

    def test_force_flag(self, runner, create_minimal_mp3):
        """Force flag is accepted."""
        filepath = create_minimal_mp3("test.mp3")
        result = runner.invoke(main, [str(filepath.parent), "--force"])
        assert "Found:" in result.output

    def test_model_size_option(self, runner, create_minimal_mp3):
        """Model size option is accepted."""
        filepath = create_minimal_mp3("test.mp3")
        result = runner.invoke(main, [str(filepath.parent), "--model-size", "tiny"])
        assert "Found:" in result.output

    def test_device_option(self, runner, create_minimal_mp3):
        """Device option is accepted."""
        filepath = create_minimal_mp3("test.mp3")
        result = runner.invoke(main, [str(filepath.parent), "--device", "cpu"])
        assert "Found:" in result.output

    def test_output_dir_option(self, runner, create_minimal_mp3):
        """Output directory option is accepted."""
        filepath = create_minimal_mp3("test.mp3")
        base_dir = filepath.parent
        output_dir = base_dir / "lrc_output"
        result = runner.invoke(main, [str(base_dir), "-o", str(output_dir)])
        assert "Found:" in result.output

    def test_language_option(self, runner, create_minimal_mp3):
        """Language option is accepted."""
        filepath = create_minimal_mp3("test.mp3")
        result = runner.invoke(main, [str(filepath.parent), "--language", "en"])
        assert "Found:" in result.output

    def test_version_flag(self, runner):
        """Version flag shows version."""
        result = runner.invoke(main, ["--version"])
        # --version triggers sys.exit(0), Click catches it as exit_code 0
        assert result.exit_code == 0
        assert "version" in result.output.lower()

    def test_quiet_flag(self, runner, create_minimal_mp3):
        """Quiet flag suppresses output."""
        filepath = create_minimal_mp3("test.mp3")
        result = runner.invoke(main, [str(filepath.parent), "--quiet"])
        # Should not show "Found:" message
        assert "Found:" not in result.output

    def test_dry_run_flag(self, runner, create_minimal_mp3):
        """Dry run flag is accepted."""
        filepath = create_minimal_mp3("test.mp3")
        result = runner.invoke(main, [str(filepath.parent), "--dry-run"])
        assert "DRY RUN" in result.output

    def test_skip_whisper_flag(self, runner, create_minimal_mp3):
        """Skip whisper flag is accepted."""
        filepath = create_minimal_mp3("test.mp3")
        result = runner.invoke(main, [str(filepath.parent), "--skip-whisper"])
        assert "Found:" in result.output

    def test_skip_lyrics_flag(self, runner, create_minimal_mp3):
        """Skip lyrics flag is accepted."""
        filepath = create_minimal_mp3("test.mp3")
        result = runner.invoke(main, [str(filepath.parent), "--skip-lyrics"])
        assert "Found:" in result.output

    def test_lrclib_only_flag(self, runner, create_minimal_mp3):
        """LRCLib only flag is accepted."""
        filepath = create_minimal_mp3("test.mp3")
        result = runner.invoke(main, [str(filepath.parent), "--lrclib-only"])
        assert "Found:" in result.output

    def test_genius_only_flag(self, runner, create_minimal_mp3):
        """Genius only flag is accepted."""
        filepath = create_minimal_mp3("test.mp3")
        result = runner.invoke(
            main,
            [str(filepath.parent), "--genius-only", "--genius-token", "test_token"],
        )
        assert "Found:" in result.output

    def test_offset_option(self, runner, create_minimal_mp3):
        """Offset option is accepted."""
        filepath = create_minimal_mp3("test.mp3")
        result = runner.invoke(main, [str(filepath.parent), "--offset", "500"])
        assert "Found:" in result.output

    def test_negative_offset_option(self, runner, create_minimal_mp3):
        """Negative offset option is accepted."""
        filepath = create_minimal_mp3("test.mp3")
        result = runner.invoke(main, [str(filepath.parent), "--offset", "-200"])
        assert "Found:" in result.output

    def test_no_metadata_flag(self, runner, create_minimal_mp3):
        """No metadata flag is accepted."""
        filepath = create_minimal_mp3("test.mp3")
        result = runner.invoke(main, [str(filepath.parent), "--no-metadata"])
        assert "Found:" in result.output

    def test_beam_size_option(self, runner, create_minimal_mp3):
        """Beam size option is accepted."""
        filepath = create_minimal_mp3("test.mp3")
        result = runner.invoke(main, [str(filepath.parent), "--beam-size", "10"])
        assert "Found:" in result.output

    def test_compute_type_option(self, runner, create_minimal_mp3):
        """Compute type option is accepted."""
        filepath = create_minimal_mp3("test.mp3")
        result = runner.invoke(main, [str(filepath.parent), "--compute-type", "float16"])
        assert "Found:" in result.output

    def test_extensions_option(self, runner, create_minimal_mp3):
        """Extensions option filters files."""
        mp3_file = create_minimal_mp3("song.mp3")
        base_dir = mp3_file.parent

        # Create FLAC file
        flac_file = base_dir / "track.flac"
        flac_file.write_bytes(b"\x66\x4c\x61\x43\x00\x00\x00\x22" + b"\x00" * 34)

        result = runner.invoke(main, [str(base_dir), "--extensions", ".mp3"])
        assert "Found:" in result.output
        assert "1 audio file" in result.output

    def test_exclude_option(self, runner, create_minimal_mp3):
        """Exclude option filters files."""
        create_minimal_mp3("normal.mp3")
        create_minimal_mp3("live_concert.mp3")
        filepath = create_minimal_mp3("test.mp3")
        base_dir = filepath.parent

        result = runner.invoke(main, [str(base_dir), "--exclude", "*live*"])
        assert "Found:" in result.output
        assert "2 audio file" in result.output

    def test_include_option(self, runner, create_minimal_mp3):
        """Include option filters files."""
        create_minimal_mp3("song.mp3")
        create_minimal_mp3("album_track.mp3")
        filepath = create_minimal_mp3("demo.mp3")
        base_dir = filepath.parent

        result = runner.invoke(main, [str(base_dir), "--include", "*album*"])
        assert "Found:" in result.output
        assert "1 audio file" in result.output

    def test_no_color_flag(self, runner, create_minimal_mp3):
        """No color flag is accepted."""
        filepath = create_minimal_mp3("test.mp3")
        result = runner.invoke(main, [str(filepath.parent), "--no-color"])
        assert "Found:" in result.output

    def test_conflicting_skip_flags(self, runner, create_minimal_mp3):
        """Cannot use both skip-whisper and skip-lyrics."""
        filepath = create_minimal_mp3("test.mp3")
        result = runner.invoke(main, [str(filepath.parent), "--skip-whisper", "--skip-lyrics"])
        assert result.exit_code == 1
        assert "cannot be used together" in result.output

    def test_conflicting_source_flags(self, runner, create_minimal_mp3):
        """Cannot use both lrclib-only and genius-only."""
        filepath = create_minimal_mp3("test.mp3")
        result = runner.invoke(main, [str(filepath.parent), "--lrclib-only", "--genius-only"])
        assert result.exit_code == 1
        assert "cannot be used together" in result.output
