
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voicebrief - Converts video / audio conversations to text and subsequently provides a summary into a manageable report.
@copyright: Copyright © 2024 Iwan van der Kleijn
@license: MIT
"""
import argparse
import os
from voicebrief.audio import partition_sound_file
from voicebrief.data import Transcript
from pathlib import Path
from voicebrief.video import video_to_audio
from voicebrief.gptapi import optimize_transcriptions, transcribe_audio

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
       
        destination_path = Path(args.destination) if args.destination is not None else None
        audio_chunks = partition_sound_file(audio_path)
        transcripts = []
        for audio_chunk in audio_chunks:
            transcript = transcribe_audio(audio_chunk, destination_path)
            transcripts.append(transcript)
                  
        print(f"""All transcripts saved to: {transcripts[0].text_path.parent}""")
        
        optimized_text = optimize_transcriptions(transcripts, destination_path)
        print(f"Optimized transcript written to: {optimized_text.text_path}")
        
    except Exception as e:
        print(e)
        exit(1)

  
if __name__ == '__main__':
    
    main()
    