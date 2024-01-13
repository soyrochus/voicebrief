
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voicebrief - Converts video / audio conversations to text and subsequently provides a summary into a manageable report.
@copyright: Copyright © 2024 Iwan van der Kleijn
@license: MIT
"""
import argparse
import os
from openai import OpenAI
from voicebrief.data import Transcript
from pathlib import Path

from voicebrief.gptapi import transcribe_audio
#https://realpython.com/playing-and-recording-sound-python/

def main():
    try:
      parser = argparse.ArgumentParser(description='Voicebrief - Converts video / audio conversations to text and subsequently provides a summary into a managable report.')
      parser.add_argument('path', type=str, help='Path to the audio file')
      parser.add_argument('destination', type=str, nargs='?', default=None, help='Optional destination directory (default: directory of audio file)')
      args = parser.parse_args()
      
      transcript = transcribe_audio(Path(args.path), args.destination)
      #transcript = transcribe_audio("test-data/audio2.mp3")
        
      print(f"""Transcription saved to {transcript.text_path}
Summary saved to {transcript.summary_path}
Summary:
{transcript.summary}
""")
    except Exception as e:
        print(e)
        exit(1)
  
if __name__ == '__main__':
    
    main()
    