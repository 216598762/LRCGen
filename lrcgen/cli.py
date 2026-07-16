"""Command-line interface for LRCGen."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn

from lrcgen.lyrics_search import search_lyrics
from lrcgen.metadata import AudioMetadata, extract_metadata, is_supported_audio
from lrcgen.whisper_sync import segments_to_lrc_lines, transcribe_audio
from lrcgen.lrc_writer import (
    create_lrc_from_lines,
    create_lrc_from_plain_text,
    create_lrc_from_synced,
    write_lrc_file,
)

console = Console()


def setup_logging(verbose: bool) -> None:
    """Configure logging with rich output."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )


def find_audio_files(path: Path, recursive: bool = True) -> list[Path]:
    """Find all supported audio files in a directory.

    Args:
        path: Directory or file path to search.
        recursive: Whether to search subdirectories.

    Returns:
        List of audio file paths.
    """
    if path.is_file():
        return [path] if is_supported_audio(path) else []

    pattern = "**/*" if recursive else "*"
    return sorted(
        p for p in path.glob(pattern)
        if p.is_file() and is_supported_audio(p)
    )


def process_audio_file(
    audio_path: Path,
    model_size: str,
    device: str,
    genius_token: str | None,
    output_dir: Path | None,
    force: bool,
    language: str | None,
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

    Returns:
        True if successful, False otherwise.
    """
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

    # Search for lyrics
    lyrics_result = search_lyrics(metadata, genius_token)

    if lyrics_result and lyrics_result.synced_lyrics:
        # Use synced lyrics from LRCLib directly
        console.print(f"  [green]Found synced lyrics from LRCLib[/green]")
        lrc_content = create_lrc_from_synced(
            lyrics_result.synced_lyrics,
            title=metadata.title or lyrics_result.title,
            artist=metadata.artist or lyrics_result.artist,
            album=metadata.album,
            duration=metadata.duration,
        )
    else:
        # Need to use Whisper for timestamps
        console.print(f"  [yellow]Using Whisper for transcription...[/yellow]")
        try:
            segments = transcribe_audio(audio_path, model_size, device, language)
        except Exception as e:
            console.print(f"  [red]Whisper transcription failed:[/red] {e}")
            return False

        if lyrics_result:
            # Align Genius lyrics with Whisper timestamps
            console.print(f"  [green]Aligning Genius lyrics with timestamps[/green]")
            timestamps = [(s.start, s.end) for s in segments]
            lrc_content = create_lrc_from_plain_text(
                lyrics_result.lyrics,
                timestamps,
                title=metadata.title or lyrics_result.title,
                artist=metadata.artist or lyrics_result.artist,
                album=metadata.album,
                duration=metadata.duration,
            )
        else:
            # No lyrics found, use Whisper transcription directly
            console.print(f"  [yellow]No lyrics found, using Whisper transcription[/yellow]")
            timestamped_lines = segments_to_lrc_lines(segments)
            lrc_content = create_lrc_from_lines(
                timestamped_lines,
                title=metadata.title,
                artist=metadata.artist,
                album=metadata.album,
                duration=metadata.duration,
            )

    # Write LRC file
    try:
        write_lrc_file(lrc_content, lrc_path)
        console.print(f"  [green]✓ Created:[/green] {lrc_path}")
        return True
    except Exception as e:
        console.print(f"  [red]Error writing LRC file:[/red] {e}")
        return False


@click.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option("-o", "--output-dir", type=click.Path(path_type=Path), help="Output directory for LRC files")
@click.option("-m", "--model-size", default="small", help="Whisper model size (tiny/base/small/medium/large-v3)")
@click.option("-d", "--device", default="cpu", help="Device for Whisper (cpu/cuda)")
@click.option("--genius-token", envvar="GENIUS_ACCESS_TOKEN", help="Genius API token")
@click.option("-r", "--recursive/--no-recursive", default=True, help="Recursively scan directories")
@click.option("-f", "--force", is_flag=True, help="Force regeneration of existing LRC files")
@click.option("-l", "--language", help="Language code for Whisper (e.g., en, es)")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
def main(
    path: Path,
    output_dir: Path | None,
    model_size: str,
    device: str,
    genius_token: str | None,
    recursive: bool,
    force: bool,
    language: str | None,
    verbose: bool,
) -> None:
    """LRCGen - Generate synchronized .LRC lyric files.

    PATH can be a single audio file or a directory to scan.
    """
    setup_logging(verbose)

    # Find audio files
    console.print(f"[bold]Scanning:[/bold] {path}")
    audio_files = find_audio_files(path, recursive)

    if not audio_files:
        console.print("[red]No supported audio files found.[/red]")
        sys.exit(1)

    console.print(f"[bold]Found:[/bold] {len(audio_files)} audio file(s)")

    # Process files
    success = 0
    failed = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Processing...", total=len(audio_files))

        for audio_path in audio_files:
            progress.update(task, description=f"Processing {audio_path.name}")
            if process_audio_file(audio_path, model_size, device, genius_token, output_dir, force, language):
                success += 1
            else:
                failed += 1
            progress.advance(task)

    # Summary
    console.print(f"\n[bold]Summary:[/bold] {success} succeeded, {failed} failed")
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
