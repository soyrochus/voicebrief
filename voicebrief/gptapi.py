#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voicebrief - Converts video / audio conversations to text and subsequently provides a summary into a manageable report.
@copyright: Copyright © 2024 Iwan van der Kleijn
@license: MIT
"""

# from moviepy.editor import AudioFileClip
from os import PathLike
import os
import pathlib
from typing import Tuple
from openai import OpenAI, OpenAIError
from pathlib import Path
from dotenv import load_dotenv

from voicebrief.data import Transcript

try:
    #set the key from file "openai_key.txt" in the same directory as this file or set the environment variable OPENAI_API_KEY
    load_dotenv("openai_api_key.env")
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
except OpenAIError as e:
    print(e)
    exit(1) 

def speech_to_text(audio_path):

    response = client.audio.transcriptions.create(
        model="whisper-1", 
        file=Path(audio_path))
    return response.text

def summarize_text(text):
  
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
        {"role": "system", "content": "You must create a summary of the provided text. Be concise and to the point."},
        {"role": "user", "content": text}
    ])
    
    return response.choices[0].message.content


def transcribe_audio(audio_path:Path, destination_dir_path = None)-> Transcript:
    
    if destination_dir_path is None:
        destination_dir_path = audio_path.parent
    
    destination_path = Path(destination_dir_path) / ("transcription_" + audio_path.name)

    # Step 1: Convert audio to text using OpenAI's speech-to-text
    audio_path = Path(audio_path)
    text = speech_to_text(audio_path)
    transcription_path = destination_path.with_suffix(".txt")
    transcription_path.write_text(text)
    
    # Step 2: Summarize the text using OpenAI's GPT-4
    summary = summarize_text(text)
    summary_path = destination_path.with_suffix(".summary.txt")
    summary_path.write_text(summary)
   
    return Transcript(text, summary, transcription_path, destination_path.with_suffix(".summary.txt"))

