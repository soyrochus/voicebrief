#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voicebrief - Converts video / audio conversations to text and subsequently provides a summary into a manageable report.
@copyright: Copyright © 2024 Iwan van der Kleijn
@license: MIT
"""
from pathlib import Path
from moviepy.editor import VideoFileClip   # type: ignore
from pydub import AudioSegment # type: ignore

def video_to_audio(video_path:Path, audio_path:Path | None = None)-> Path:
    
    if audio_path is None:
        audio_path = Path(video_path).with_suffix(".wav")
        
    video_clip = VideoFileClip(str(video_path))
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(audio_path)

    # Load your audio file
    audio = AudioSegment.from_file(audio_path)

    # Export as MP3
    mp3_path = Path(audio_path).with_suffix(".mp3")
    audio.export(mp3_path, format="mp3", bitrate="128k")
    
    return mp3_path