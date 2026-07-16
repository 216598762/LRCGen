"""Command-line interface for LRCGen."""

from __future__ import annotations

import logging
import sys
from fnmatch import fnmatch
from pathlib import Path

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn

from lrcgen import __version__
from lrcgen.lrc_writer import (
    create_lrc_from_lines,
    create_lrc_from_plain_text,
    create_lrc_from_synced,
    write_lrc_file,
)
from lrcgen.lyrics_search import search_lyrics
from lrcgen.metadata import extract_metadata, is_supported_audio
from lrcgen.whisper_sync import segments_to_lrc_lines, transcribe_audio

_console = Console()


def get_console() -> Console:
    """Get the console instance."""
    return _console


def setup_logging(verbose: bool, quiet: bool) -> None:
    """Configure logging with rich output.

    Args:
        verbose: Enable debug logging.
        quiet: Suppress info-level logs (only errors shown).
    """
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=get_console(), rich_tracebacks=True)],
    )


def find_audio_files(
    path: Path,
    recursive: bool = True,
    extensions: str | None = None,
    exclude_patterns: list[str] | None = None,
    include_patterns: list[str] | None = None,
) -> list[Path]:
    """Find all supported audio files in a directory.

    Args:
        path: Directory or file path to search.
        recursive: Whether to search subdirectories.
        extensions: Comma-separated list of extensions to include (e.g., ".mp3,.flac").
        exclude_patterns: Glob patterns to exclude (e.g., "*.temp.*").
        include_patterns: Glob patterns to include (only matching files processed).

    Returns:
        List of audio file paths.
    """
    if path.is_file():
        if extensions:
            allowed = {ext.strip().lower() for ext in extensions.split(",")}
            return [path] if path.suffix.lower() in allowed else []
        return [path] if is_supported_audio(path) else []

    # Build glob patterns based on extensions
    if extensions:
        allowed = {ext.strip().lower() for ext in extensions.split(",")}
        audio_files = []
        pattern = "**/*" if recursive else "*"
        for p in path.glob(pattern):
            if not p.is_file():
                continue
            if p.suffix.lower() not in allowed:
                continue
            audio_files.append(p)
    else:
        pattern = "**/*" if recursive else "*"
        audio_files = sorted(p for p in path.glob(pattern) if p.is_file() and is_supported_audio(p))

    # Apply include patterns (only keep matching files)
    if include_patterns:
        filtered = []
        for p in audio_files:
            for pat in include_patterns:
                if fnmatch(p.name, pat) or fnmatch(str(p), pat):
                    filtered.append(p)
                    break
        audio_files = filtered

    # Apply exclude patterns
    if exclude_patterns:
        filtered = []
        for p in audio_files:
            excluded = False
            for pat in exclude_patterns:
                if fnmatch(p.name, pat) or fnmatch(str(p), pat):
                    excluded = True
                    break
            if not excluded:
                filtered.append(p)
        audio_files = filtered

    return sorted(audio_files)


def process_audio_file(
    audio_path: Path,
    model_size: str,
    device: str,
    genius_token: str | None,
    output_dir: Path | None,
    force: bool,
    language: str | None,
    skip_whisper: bool = False,
    skip_lyrics: bool = False,
    lrclib_only: bool = False,
    genius_only: bool = False,
    offset_ms: int = 0,
    no_metadata: bool = False,
    beam_size: int = 5,
    compute_type: str = "int8",
    dry_run: bool = False,
) -> bool:
    """Process a single audio file.

    Args:
        audio_path: Path to the audio file.
        model_size: Whisper model size.
        device: Device for Whisper.
        genius_token: Genius API token.
        output_dir: Optional output directory.
        force: Force regeneration even if LRC exists.
        language: Optional language code.
        skip_whisper: Skip Whisper transcription (use online lyrics only).
        skip_lyrics: Skip lyrics search (use Whisper transcription only).
        lrclib_only: Only search LRCLib (skip Genius).
        genius_only: Only search Genius (skip LRCLib).
        offset_ms: Global time offset in milliseconds to apply.
        no_metadata: Don't include metadata tags in LRC file.
        beam_size: Whisper beam size.
        compute_type: Whisper compute type (int8, float16, float32).
        dry_run: Preview without processing.

    Returns:
        True if successful, False otherwise.
    """
    console = get_console()
    console.print(f"\n[bold blue]Processing:[/bold blue] {audio_path.name}")

    # Determine output path
    if output_dir:
        lrc_path = output_dir / audio_path.with_suffix(".lrc").name
    else:
        lrc_path = audio_path.with_suffix(".lrc")

    # Check if LRC already exists
    if lrc_path.exists() and not force:
        console.print(f"  [dim]LRC file already exists, skipping: {lrc_path.name}[/dim]")
        return True

    # Extract metadata
    try:
        metadata = extract_metadata(audio_path)
        console.print(f"  [green]Metadata:[/green] {metadata.artist} - {metadata.title}")
    except Exception as e:
        console.print(f"  [red]Error extracting metadata:[/red] {e}")
        return False

    # Dry run mode
    if dry_run:
        console.print(f"  [yellow]Would write:[/yellow] {lrc_path}")
        return True

    # Search for lyrics
    lyrics_result = None
    if not skip_lyrics:
        if lrclib_only:
            from lrcgen.lyrics_search import search_lrclib

            lyrics_result = search_lrclib(metadata)
        elif genius_only:
            from lrcgen.lyrics_search import search_genius

            lyrics_result = search_genius(metadata, genius_token)
        else:
            lyrics_result = search_lyrics(metadata, genius_token)

    lrc_content = None

    if lyrics_result and lyrics_result.synced_lyrics:
        # Use synced lyrics from LRCLib directly
        console.print("  [green]Found synced lyrics from LRCLib[/green]")
        title = metadata.title if no_metadata else (metadata.title or lyrics_result.title)
        artist = metadata.artist if no_metadata else (metadata.artist or lyrics_result.artist)
        album = None if no_metadata else metadata.album
        lrc_content = create_lrc_from_synced(
            lyrics_result.synced_lyrics,
            title=title,
            artist=artist,
            album=album,
            duration=metadata.duration,
        )
    else:
        # Need to use Whisper for timestamps
        if skip_whisper:
            console.print("  [red]No synced lyrics found and Whisper is disabled.[/red]")
            return False

        console.print("  [yellow]Using Whisper for transcription...[/yellow]")
        try:
            segments = transcribe_audio(
                audio_path,
                model_size,
                device,
                language,
                beam_size=beam_size,
                compute_type=compute_type,
            )
        except Exception as e:
            console.print(f"  [red]Whisper transcription failed:[/red] {e}")
            return False

        if not segments:
            console.print("  [red]Whisper returned no segments (non-vocal audio?)[/red]")
            return False

        if lyrics_result:
            # Align Genius lyrics with Whisper timestamps
            console.print("  [green]Aligning Genius lyrics with timestamps[/green]")
            timestamps = [(s.start, s.end) for s in segments]
            title = metadata.title if no_metadata else (metadata.title or lyrics_result.title)
            artist = metadata.artist if no_metadata else (metadata.artist or lyrics_result.artist)
            album = None if no_metadata else metadata.album
            lrc_content = create_lrc_from_plain_text(
                lyrics_result.lyrics,
                timestamps,
                title=title,
                artist=artist,
                album=album,
                duration=metadata.duration,
            )
        else:
            # No lyrics found, use Whisper transcription directly
            console.print("  [yellow]No lyrics found, using Whisper transcription[/yellow]")
            timestamped_lines = segments_to_lrc_lines(segments)
            title = metadata.title if no_metadata else metadata.title
            artist = metadata.artist if no_metadata else metadata.artist
            album = None if no_metadata else metadata.album
            lrc_content = create_lrc_from_lines(
                timestamped_lines,
                title=title,
                artist=artist,
                album=album,
                duration=metadata.duration,
            )

    # Apply offset if specified
    if offset_ms != 0 and lrc_content:
        import re

        def adjust_timestamp(match: re.Match) -> str:
            mm = int(match.group(1))
            ss = int(match.group(2))
            ms = int(match.group(3))
            total_ms = mm * 60000 + ss * 1000 + ms + offset_ms
            if total_ms < 0:
                total_ms = 0
            new_mm = total_ms // 60000
            new_ss = (total_ms % 60000) // 1000
            new_ms = total_ms % 1000
            return f"[{new_mm:02d}:{new_ss:02d}.{new_ms:03d}]"

        lrc_content = re.sub(r"\[(\d{2}):(\d{2})\.(\d{2,3})\]", adjust_timestamp, lrc_content)

    # Write LRC file
    try:
        write_lrc_file(lrc_content, lrc_path)
        console.print(f"  [green]✓ Created:[/green] {lrc_path}")
        return True
    except Exception as e:
        console.print(f"  [red]Error writing LRC file:[/red] {e}")
        return False


@click.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path), required=False)
@click.version_option(version=__version__, prog_name="lrcgen")
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(path_type=Path),
    help="Output directory for LRC files.",
)
@click.option(
    "-m",
    "--model-size",
    default="small",
    show_default=True,
    help="Whisper model size (tiny, base, small, medium, large-v3).",
)
@click.option(
    "-d",
    "--device",
    default="cpu",
    show_default=True,
    help="Device for Whisper (cpu, cuda, auto).",
)
@click.option(
    "--genius-token",
    envvar="GENIUS_ACCESS_TOKEN",
    help="Genius API token (or set GENIUS_ACCESS_TOKEN env var).",
)
@click.option(
    "-r",
    "--recursive/--no-recursive",
    default=True,
    show_default=True,
    help="Recursively scan directories.",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Force regeneration of existing LRC files.",
)
@click.option(
    "-l",
    "--language",
    help="Language code for Whisper (e.g., en, es, ja). Auto-detect if not set.",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose debug logging.",
)
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    help="Suppress output except errors.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview what would be done without processing files.",
)
@click.option(
    "--skip-whisper",
    is_flag=True,
    help="Skip Whisper transcription (only use online lyrics).",
)
@click.option(
    "--skip-lyrics",
    is_flag=True,
    help="Skip lyrics search (only use Whisper transcription).",
)
@click.option(
    "--lrclib-only",
    is_flag=True,
    help="Only search LRCLib (skip Genius fallback).",
)
@click.option(
    "--genius-only",
    is_flag=True,
    help="Only search Genius (skip LRCLib).",
)
@click.option(
    "--offset",
    type=int,
    default=0,
    show_default=True,
    help="Global time offset in milliseconds (positive delays, negative advances).",
)
@click.option(
    "--no-metadata",
    is_flag=True,
    help="Don't include metadata tags (title, artist, album) in LRC.",
)
@click.option(
    "--beam-size",
    type=int,
    default=5,
    show_default=True,
    help="Whisper beam size for transcription.",
)
@click.option(
    "--compute-type",
    default="int8",
    show_default=True,
    type=click.Choice(["int8", "float16", "float32"], case_sensitive=False),
    help="Whisper compute type (int8=fast, float16=gpu, float32=best quality).",
)
@click.option(
    "--extensions",
    default=None,
    help="Comma-separated audio extensions to include (default: all supported).",
)
@click.option(
    "--exclude",
    multiple=True,
    help="Glob patterns to exclude (can be specified multiple times).",
)
@click.option(
    "--include",
    "include_patterns",
    multiple=True,
    help="Glob patterns to include (can be specified multiple times).",
)
@click.option(
    "--no-color",
    is_flag=True,
    help="Disable colored output.",
)
def main(
    path: str | None,
    output_dir: Path | None,
    model_size: str,
    device: str,
    genius_token: str | None,
    recursive: bool,
    force: bool,
    language: str | None,
    verbose: bool,
    quiet: bool,
    dry_run: bool,
    skip_whisper: bool,
    skip_lyrics: bool,
    lrclib_only: bool,
    genius_only: bool,
    offset: int,
    no_metadata: bool,
    beam_size: int,
    compute_type: str,
    extensions: str | None,
    exclude: tuple[str, ...],
    include_patterns: tuple[str, ...],
    no_color: bool,
) -> None:
    """LRCGen - Generate synchronized .LRC lyric files.

    PATH can be a single audio file or a directory to scan.

    \b
    Examples:
      lrcgen song.mp3
      lrcgen /path/to/music/ --model-size medium --device cuda
      lrcgen music/ --dry-run --verbose
      lrcgen music/ --skip-whisper --genius-only
    """
    global _console

    # Handle no-color
    if no_color:
        _console = Console(no_color=True)

    # Require PATH
    if path is None:
        get_console().print("[red]Error: PATH argument is required.[/red]")
        sys.exit(1)

    path_obj = Path(path)

    # Validate conflicting options
    if skip_whisper and skip_lyrics:
        get_console().print(
            "[red]Error: --skip-whisper and --skip-lyrics cannot be used together.[/red]"
        )
        sys.exit(1)

    if lrclib_only and genius_only:
        get_console().print(
            "[red]Error: --lrclib-only and --genius-only cannot be used together.[/red]"
        )
        sys.exit(1)

    setup_logging(verbose, quiet)

    # Find audio files
    if not quiet:
        get_console().print(f"[bold]Scanning:[/bold] {path_obj}")
    audio_files = find_audio_files(
        path_obj,
        recursive,
        extensions=extensions,
        exclude_patterns=list(exclude) if exclude else None,
        include_patterns=list(include_patterns) if include_patterns else None,
    )

    if not audio_files:
        get_console().print("[red]No supported audio files found.[/red]")
        sys.exit(1)

    if not quiet:
        get_console().print(f"[bold]Found:[/bold] {len(audio_files)} audio file(s)")

    if dry_run:
        get_console().print("[yellow]DRY RUN - no files will be modified[/yellow]")

    # Process files
    success = 0
    failed = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=get_console(),
    ) as progress:
        task = progress.add_task("Processing...", total=len(audio_files))

        for audio_path in audio_files:
            if not quiet:
                progress.update(task, description=f"Processing {audio_path.name}")
            if process_audio_file(
                audio_path,
                model_size,
                device,
                genius_token,
                output_dir,
                force,
                language,
                skip_whisper=skip_whisper,
                skip_lyrics=skip_lyrics,
                lrclib_only=lrclib_only,
                genius_only=genius_only,
                offset_ms=offset,
                no_metadata=no_metadata,
                beam_size=beam_size,
                compute_type=compute_type,
                dry_run=dry_run,
            ):
                success += 1
            else:
                failed += 1
            progress.advance(task)

    # Summary
    if not quiet:
        get_console().print(f"\n[bold]Summary:[/bold] {success} succeeded, {failed} failed")
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
