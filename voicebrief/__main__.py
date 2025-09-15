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

from voicebrief.app import run_voicebrief
from voicebrief.logging_utils import configure_logging


def main(argv: list[str] | None = None) -> None:
    try:
        parser = argparse.ArgumentParser(
            description="""Voicebrief - Converts video / audio conversations
to text and subsequently provides a summary into a managable report."""
        )
        parser.add_argument("path", type=str, nargs="?", help="Path to the media file")
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
        parser.add_argument(
            "-g",
            "--gui",
            action="store_true",
            help="Launch the graphical interface (no other arguments allowed)",
        )
        args = parser.parse_args(argv)

        if args.gui:
            if any(
                value
                for value in (
                    args.path,
                    args.destination,
                    args.video,
                    args.verbose,
                    args.log_level,
                )
            ):
                parser.error("--gui cannot be combined with other arguments.")

            from voicebrief.gui import launch_gui  # Lazy import

            launch_gui()
            return

        if not args.path:
            parser.error("the following arguments are required: path")

        # Configure logging
        level = "DEBUG" if args.verbose else args.log_level
        configure_logging(level)
        log = logging.getLogger("voicebrief.cli")
        log.debug("CLI started with args: %s", vars(args))

        result = run_voicebrief(
            Path(args.path),
            destination=Path(args.destination) if args.destination else None,
            force_video=args.video,
            auto_detect_video=True,
            logger=log,
        )

        log.info("Processing complete for %s", result.source_path)
        log.info("Optimized transcript available at %s", result.optimized_transcript.text_path)

    except Exception as e:
        if os.environ.get("VOICEBRIEF_LOG_LEVEL", "").upper() == "DEBUG":
            logging.getLogger("voicebrief").exception("Unhandled error")
        else:
            logging.getLogger("voicebrief").error("%s", e)
        exit(1)


if __name__ == "__main__":

    main()
