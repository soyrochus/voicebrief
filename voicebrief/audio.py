#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voicebrief - Converts video / audio conversations to text and subsequently provides a summary into a manageable report.
@copyright: Copyright © 2024 Iwan van der Kleijn
@license: MIT
"""
from pydub import AudioSegment  # type: ignore
from pathlib import Path
from typing import List

import subprocess
from pathlib import Path
from typing import List

def partition_sound_file(audio_path: Path, max_chunk_size_mb: int = 20) -> List[Path]:
    # Define the chunk size in bytes
    max_chunk_size_bytes = max_chunk_size_mb * 1024 * 1024
    
    #if size audio_path is snaller than max_chunk_size_bytes, return audio_path
    #as chunking it would be unnecessary
    if audio_path.stat().st_size < max_chunk_size_bytes:
        return [audio_path]
    
    # The output directory for chunks
    output_dir = audio_path.parent / (audio_path.stem + "_chunks")
    output_dir.mkdir(exist_ok=True)
    
    # The base command for ffmpeg
    base_command = [
        'ffmpeg',
        '-i', str(audio_path),
        '-f', 'segment',
        '-segment_time', str(max_chunk_size_mb * 60), # Approximate maximum duration of each file in seconds
        '-c', 'copy',
        '-break_non_keyframes', '1',
        '-reset_timestamps', '1',
        str(output_dir / f"{audio_path.stem}_%03d{audio_path.suffix}")
    ]

    # Execute the command
    result = subprocess.run(base_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Check for errors
    if result.returncode != 0:
        raise Exception(f"Error splitting file: {result.stderr.decode('utf-8')}")

    # List the created files
    paths = list(output_dir.glob(f"{audio_path.stem}_*{audio_path.suffix}"))
    
    return paths
