"""High-level orchestration helpers for running Voicebrief workflows."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING
import logging

from voicebrief.audio import partition_sound_file

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from voicebrief.data import Transcript

_VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".webm"}


@dataclass(frozen=True)
class VoicebriefResult:
    """Outcome of processing a single media source."""

    source_path: Path
    audio_path: Path
    transcripts: List["Transcript"]
    optimized_transcript: "Transcript"
    extracted_audio: bool


def run_voicebrief(
    source_path: Path | str,
    destination: Path | str | None = None,
    force_video: bool = False,
    auto_detect_video: bool = True,
    logger: Optional[logging.Logger] = None,
) -> VoicebriefResult:
    """Run the Voicebrief pipeline for a media file.

    Parameters
    ----------
    source_path:
        File to process (audio or video).
    destination:
        Optional directory where output text files are written.
    force_video:
        Treat ``source_path`` as a video even if the extension is unknown.
    auto_detect_video:
        When ``True`` and ``force_video`` is ``False``, rely on file extension
        detection to decide if audio needs to be extracted from the video first.
    logger:
        Optional logger to record progress. When ``None`` the module logger is
        used.
    """

    log = logger or logging.getLogger("voicebrief.app")

    src_path = Path(source_path).expanduser()
    if not src_path.exists():
        raise FileNotFoundError(f"File {src_path} does not exist")
    src_path = src_path.resolve()
    dest_path = Path(destination).expanduser() if destination else None
    if dest_path is not None:
        if dest_path.exists() and not dest_path.is_dir():
            raise NotADirectoryError(f"Destination must be a directory: {dest_path}")
        dest_path.mkdir(parents=True, exist_ok=True)

    needs_extraction = force_video
    if not needs_extraction and auto_detect_video:
        needs_extraction = src_path.suffix.lower() in _VIDEO_EXTENSIONS

    if needs_extraction:
        log.info("Extracting audio from video: %s", src_path)
        from voicebrief.video import video_to_audio  # Lazy import

        audio_path = video_to_audio(src_path)
        log.info("Audio extracted to: %s", audio_path)
    else:
        audio_path = src_path

    log.debug("Partitioning audio: %s", audio_path)
    audio_chunks = partition_sound_file(audio_path)
    log.info("Processing %d audio chunk(s)", len(audio_chunks))

    from voicebrief.gptapi import optimize_transcriptions, transcribe_audio

    transcripts: List["Transcript"] = []
    for chunk in audio_chunks:
        log.info("Transcribing chunk: %s", chunk)
        transcript = transcribe_audio(chunk, dest_path)
        transcripts.append(transcript)

    if not transcripts:
        raise RuntimeError("No transcripts generated. Check the input media file.")

    log.info("All transcripts saved to: %s", transcripts[0].text_path.parent)
    optimized = optimize_transcriptions(transcripts, dest_path)
    log.info("Optimized transcript written to: %s", optimized.text_path)

    return VoicebriefResult(
        source_path=src_path,
        audio_path=audio_path,
        transcripts=transcripts,
        optimized_transcript=optimized,
        extracted_audio=needs_extraction,
    )
