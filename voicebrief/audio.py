#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voicebrief - Converts video / audio conversations to text and subsequently provides a summary into a manageable report.
@copyright: Copyright © 2024 Iwan van der Kleijn
@license: MIT
"""

from pathlib import Path
from typing import List
import subprocess
import logging
import math


def partition_sound_file(audio_path: Path, max_chunk_size_mb: int = 20) -> List[Path]:
    max_chunk_size_bytes = max_chunk_size_mb * 1024 * 1024
    return _partition_sound_file(audio_path, max_chunk_size_bytes)


def _partition_sound_file(audio_path: Path, max_chunk_size_bytes: int) -> List[Path]:
    log = logging.getLogger("voicebrief.audio")

    # if size audio_path is snaller than max_chunk_size_bytes, return audio_path
    # as chunking it would be unnecessary
    size = audio_path.stat().st_size
    if size < max_chunk_size_bytes:
        log.debug(
            "Skipping chunking: size=%dB < max=%dB (%s)",
            size,
            max_chunk_size_bytes,
            audio_path,
        )
        return [audio_path]

    # The output directory for chunks
    output_dir = audio_path.parent / (audio_path.stem + "_chunks")
    output_dir.mkdir(exist_ok=True)

    segment_seconds = _estimate_segment_duration_seconds(
        audio_path, max_chunk_size_bytes
    )

    # The base command for ffmpeg
    base_command = [
        "ffmpeg",
        "-i",
        str(audio_path),
        "-f",
        "segment",
        "-segment_time",
        str(segment_seconds),
        "-c",
        "copy",
        "-break_non_keyframes",
        "1",
        "-reset_timestamps",
        "1",
        str(output_dir / f"{audio_path.stem}_%03d{audio_path.suffix}"),
    ]

    log.debug("Running ffmpeg: %s", " ".join(base_command))
    # Execute the command
    result = subprocess.run(
        base_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # Check for errors
    if result.returncode != 0:
        err = result.stderr.decode("utf-8", errors="replace")
        log.error("ffmpeg failed (code %s): %s", result.returncode, err)
        raise Exception(f"Error splitting file: {err}")

    # List the created files and sort them to ensure correct order
    paths = sorted(output_dir.glob(f"{audio_path.stem}_*{audio_path.suffix}"))
    log.debug("Created %d chunk(s) in %s", len(paths), output_dir)

    if not paths:
        raise RuntimeError(f"ffmpeg created no chunks for {audio_path}")

    return _resplit_oversized_chunks(paths, max_chunk_size_bytes, log)


def _probe_duration_seconds(audio_path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nokey=1:noprint_wrappers=1",
            str(audio_path),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        err = result.stderr.strip()
        raise RuntimeError(f"ffprobe failed for {audio_path}: {err}")

    output = result.stdout.strip()
    if not output:
        raise RuntimeError(f"ffprobe returned no duration for {audio_path}")

    duration_seconds = float(output)
    if duration_seconds <= 0:
        raise RuntimeError(f"Invalid duration {duration_seconds} for {audio_path}")
    return duration_seconds


def _calculate_segment_duration_seconds(
    file_size_bytes: int,
    duration_seconds: float,
    max_chunk_size_bytes: int,
    safety_factor: float = 0.85,
) -> int:
    if file_size_bytes <= 0:
        raise ValueError("file_size_bytes must be positive")
    if duration_seconds <= 0:
        raise ValueError("duration_seconds must be positive")
    if max_chunk_size_bytes <= 0:
        raise ValueError("max_chunk_size_bytes must be positive")
    if not 0 < safety_factor < 1:
        raise ValueError("safety_factor must be between 0 and 1")

    bytes_per_second = file_size_bytes / duration_seconds
    target_chunk_bytes = max_chunk_size_bytes * safety_factor
    segment_seconds = math.floor(target_chunk_bytes / bytes_per_second)
    return max(1, min(math.floor(duration_seconds), segment_seconds))


def _estimate_segment_duration_seconds(
    audio_path: Path, max_chunk_size_bytes: int
) -> int:
    log = logging.getLogger("voicebrief.audio")
    size_bytes = audio_path.stat().st_size
    duration_seconds = _probe_duration_seconds(audio_path)
    segment_seconds = _calculate_segment_duration_seconds(
        size_bytes,
        duration_seconds,
        max_chunk_size_bytes,
    )
    log.debug(
        "Estimated segment duration=%ss for %s (size=%dB duration=%.2fs limit=%dB)",
        segment_seconds,
        audio_path,
        size_bytes,
        duration_seconds,
        max_chunk_size_bytes,
    )
    return segment_seconds


def _resplit_oversized_chunks(
    paths: List[Path], max_chunk_size_bytes: int, log: logging.Logger
) -> List[Path]:
    final_paths: List[Path] = []
    for path in paths:
        size = path.stat().st_size
        if size <= max_chunk_size_bytes:
            final_paths.append(path)
            continue

        log.warning(
            "Chunk exceeds limit after splitting; resplitting %s (size=%dB limit=%dB)",
            path,
            size,
            max_chunk_size_bytes,
        )
        resplit_paths = _partition_sound_file(path, max_chunk_size_bytes)
        if len(resplit_paths) == 1 and resplit_paths[0] == path:
            raise RuntimeError(f"Unable to reduce oversized chunk: {path}")
        final_paths.extend(resplit_paths)

    return final_paths
