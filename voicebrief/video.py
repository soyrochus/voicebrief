#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voicebrief - Converts video / audio conversations to text and subsequently provides a summary into a manageable report.
@copyright: Copyright © 2024 Iwan van der Kleijn
@license: MIT
"""
from pathlib import Path
import logging


def video_to_audio(video_path: Path, audio_path: Path | None = None) -> Path:

    if audio_path is None:
        audio_path = Path(video_path).with_suffix(".wav")

    # Lazy imports so that simply importing the package (e.g., --help)
    # does not require multimedia deps on all platforms
    from moviepy.editor import VideoFileClip  # type: ignore

    try:
        from pydub import AudioSegment  # type: ignore
    except ModuleNotFoundError as e:
        # Provide a clearer error when Python 3.13 removes stdlib audioop
        raise ModuleNotFoundError(
            "Missing dependency for audio processing. Install 'pydub' and, on Python 3.13, the 'audioop-lts' backport. "
            "Also ensure ffmpeg is installed and on PATH."
        ) from e

    log = logging.getLogger("voicebrief.video")
    log.debug("Loading video: %s", video_path)
    video_clip = VideoFileClip(str(video_path))
    audio_clip = video_clip.audio
    log.debug("Writing extracted WAV to: %s", audio_path)
    audio_clip.write_audiofile(str(audio_path))

    # Load your audio file
    log.debug("Converting WAV to MP3")
    audio = AudioSegment.from_file(str(audio_path))

    # Export as MP3
    mp3_path = Path(audio_path).with_suffix(".mp3")
    audio.export(str(mp3_path), format="mp3", bitrate="128k")
    log.debug("MP3 written to: %s", mp3_path)

    return mp3_path
