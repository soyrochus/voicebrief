#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voicebrief - Converts video / audio conversations to text and subsequently provides a summary into a manageable report.
@copyright: Copyright © 2024 Iwan van der Kleijn
@license: MIT
"""
import argparse
import logging
import os
from pathlib import Path
from voicebrief.audio import partition_sound_file
from voicebrief.gptapi import optimize_transcriptions, transcribe_audio
from voicebrief.logging_utils import configure_logging


def main():
    try:
        parser = argparse.ArgumentParser(
            description="""Voicebrief - Converts video / audio conversations
to text and subsequently provides a summary into a managable report."""
        )
        parser.add_argument("path", type=str, help="Path to the audio file")
        parser.add_argument(
            "destination",
            type=str,
            nargs="?",
            default=None,
            help='Optional destination directory (default: directory of "path" parameter)',
        )
        parser.add_argument(
            "-v",
            "--video",
            action="store_true",
            help='Consider "path" to be a video and extract the audio',
        )
        parser.add_argument(
            "-V",
            "--verbose",
            action="store_true",
            help="Enable verbose debug logging (same as --log-level DEBUG)",
        )
        parser.add_argument(
            "--log-level",
            choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
            default=None,
            help="Set log level. Env fallback: VOICEBRIEF_LOG_LEVEL.",
        )
        args = parser.parse_args()

        # Configure logging
        level = "DEBUG" if args.verbose else args.log_level
        configure_logging(level)
        log = logging.getLogger("voicebrief.cli")
        log.debug("CLI started with args: %s", vars(args))

        path = Path(args.path)
        if path is None or not path.exists():
            raise FileNotFoundError(f"File {path} does not exist")

        # Auto-detect video by extension if --video not passed
        video_exts = {".mp4", ".mov", ".mkv", ".avi", ".webm"}
        is_video = path.suffix.lower() in video_exts

        if args.video or is_video:
            # Lazy import to avoid importing heavy/optional deps for --help or audio-only flows
            from voicebrief.video import video_to_audio

            if not args.video and is_video:
                log.info(
                    "Detected video file by extension (%s). Extracting audio.",
                    path.suffix.lower(),
                )
            log.info("Extracting audio from video: %s", path)
            audio_path = video_to_audio(path)
            log.info("Audio extracted from %s to %s", path, audio_path)
        else:
            audio_path = Path(args.path)

        destination_path = (
            Path(args.destination) if args.destination is not None else None
        )
        log.debug("Destination path: %s", destination_path)
        audio_chunks = partition_sound_file(audio_path)
        log.info("Processing %d audio chunk(s)", len(audio_chunks))
        transcripts = []
        for audio_chunk in audio_chunks:
            log.info("Transcribing chunk: %s", audio_chunk)
            transcript = transcribe_audio(audio_chunk, destination_path)
            transcripts.append(transcript)

        log.info("All transcripts saved to: %s", transcripts[0].text_path.parent)

        optimized_text = optimize_transcriptions(transcripts, destination_path)
        log.info("Optimized transcript written to: %s", optimized_text.text_path)

    except Exception as e:
        if os.environ.get("VOICEBRIEF_LOG_LEVEL", "").upper() == "DEBUG":
            logging.getLogger("voicebrief").exception("Unhandled error")
        else:
            logging.getLogger("voicebrief").error("%s", e)
        exit(1)


if __name__ == "__main__":

    main()
