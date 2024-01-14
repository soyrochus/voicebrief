
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voicebrief - Converts video / audio conversations to text and subsequently provides a summary into a manageable report.
@copyright: Copyright © 2024 Iwan van der Kleijn
@license: MIT
"""
import argparse
import os
from voicebrief.data import Transcript
from pathlib import Path
from voicebrief.video import video_to_audio
from voicebrief.gptapi import transcribe_audio

#https://realpython.com/playing-and-recording-sound-python/

def main():
    try:
        parser = argparse.ArgumentParser(description='Voicebrief - Converts video / audio conversations to text and subsequently provides a summary into a managable report.')
        parser.add_argument('path', type=str, help='Path to the audio file')
        parser.add_argument('destination', type=str, nargs='?', default=None, help='Optional destination directory (default: directory of "path" parameter)')
        parser.add_argument('-v', '--video', action='store_true', help='Consider "path" to be a video and extract the audio')
        args = parser.parse_args()
      
        path = Path(args.path)
        if path is None or not path.exists():
            raise FileNotFoundError(f"File {path} does not exist")
        
        if args.video:
            audio_path = video_to_audio(path)
            print(f"Audio extracted from {path} to {audio_path}") 
        else:   
            audio_path = Path(args.path)
        
        transcript = transcribe_audio(audio_path, Path(args.destination) if args.destination is not None else None)
        print(f"""Transcription saved to {transcript.text_path}
Summary saved to {transcript.summary_path}
Summary:
{transcript.summary}
""")
    except Exception as e:
        print(e)
        exit(1)
 
# def test():
#     from moviepy.editor import VideoFileClip   # type: ignore

#     video_path = 'test-data/guia design software.mp4'
#     audio_path = Path(video_path).with_suffix(".wav")
#     video_clip = VideoFileClip(video_path)
#     audio_clip = video_clip.audio
#     audio_clip.write_audiofile(audio_path)
    
#     from pydub import AudioSegment # type: ignore

#     # Load your audio file
#     audio = AudioSegment.from_file(audio_path)

#     # Export as MP3
#     mp3_path = Path(audio_path).with_suffix(".mp3")
#     audio.export(mp3_path, format="mp3", bitrate="128k")

    
  
if __name__ == '__main__':
    
    main()
    