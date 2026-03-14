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


def _load_custom_instructions(args: argparse.Namespace) -> str | None:
    if args.custom_instructions and args.prompt_file:
        raise ValueError("Use either --custom-instructions or --prompt-file, not both.")

    if args.custom_instructions:
        return args.custom_instructions.strip() or None

    if args.prompt_file:
        prompt_path = Path(args.prompt_file).expanduser()
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file does not exist: {prompt_path}")
        if not prompt_path.is_file():
            raise ValueError(f"Prompt path is not a file: {prompt_path}")
        return prompt_path.read_text(encoding="utf-8").strip() or None

    return None


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
            "-m",
            "--markdown",
            action="store_true",
            help="Generate a full human-readable markdown transcript with highest fidelity",
        )
        parser.add_argument(
            "-o",
            "--optimized",
            action="store_true",
            help="Generate optimized transcript (processed and structured version)",
        )
        parser.add_argument(
            "-V",
            "--verbose",
            action="store_true",
            help="Enable verbose debug logging (same as --log-level DEBUG)",
        )
        parser.add_argument(
            "--custom-instructions",
            type=str,
            default=None,
            help="Append additional instructions to the built-in LLM prompt.",
        )
        parser.add_argument(
            "--prompt-file",
            type=str,
            default=None,
            help="Read additional LLM instructions from a UTF-8 text file.",
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
                    args.markdown,
                    args.optimized,
                    args.verbose,
                    args.custom_instructions,
                    args.prompt_file,
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
        custom_instructions = _load_custom_instructions(args)

        result = run_voicebrief(
            Path(args.path),
            destination=Path(args.destination) if args.destination else None,
            force_video=args.video,
            auto_detect_video=True,
            generate_markdown=args.markdown,
            generate_optimized=args.optimized,
            custom_instructions=custom_instructions,
            logger=log,
        )

        log.info("Processing complete for %s", result.source_path)
        if result.optimized_transcript:
            log.info("Optimized transcript available at %s", result.optimized_transcript.text_path)
        if result.markdown_transcript:
            log.info("Markdown transcript available at %s", result.markdown_transcript.text_path)

    except Exception as e:
        if os.environ.get("VOICEBRIEF_LOG_LEVEL", "").upper() == "DEBUG":
            logging.getLogger("voicebrief").exception("Unhandled error")
        else:
            logging.getLogger("voicebrief").error("%s", e)
        exit(1)


if __name__ == "__main__":

    main()
