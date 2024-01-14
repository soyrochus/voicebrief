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
from typing import List, Tuple
from openai import OpenAI, OpenAIError
from pathlib import Path
from dotenv import load_dotenv
import tiktoken

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

    audio_path = Path(audio_path)
    
    text = speech_to_text(audio_path)
    transcription_path = destination_path.with_suffix(".txt")
   
    transcript = Transcript.to_file(text, transcription_path)
    print(f"Transcript written to: {transcript.text_path}")
    return transcript

def optimize_transcriptions(transcripts: List[Transcript], destination_path: Path | None = None) -> Transcript:
    """Add the text of all transcript and then calculate the total token size of the text using the tiktoken library """
    # To get the tokeniser corresponding to a specific model in the OpenAI API:
    enc = tiktoken.encoding_for_model("gpt-4")
    text = ""
    total_tokens = 0
    responses = []
    for transcript in transcripts:
        tokens = enc.encode(transcript.text)
        if total_tokens + len(tokens) > 4000:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content":"Please verify, optionally correct and organize the following text into a coherent and well-structured format with clear, distinct paragraphs. Each paragraph should have a logical flow and connection to the next, maintaining consistency and clarity throughout the text. Paragraphs should be delimted with an empty line."},
                    {"role": "user", "content": text}
                ])
            responses.append(response.choices[0].message.content) #type: ignore
            text = transcript.text
            total_tokens = len(tokens)
        else:
            text += transcript.text + " "
            total_tokens += len(tokens)
    
    if text:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content":"Please verify, optionally correct and organize the following text into a coherent and well-structured format with clear, distinct paragraphs. Each paragraph should have a logical flow and connection to the next, maintaining consistency and clarity throughout the text. Paragraphs should be delimted with an empty line."},
                {"role": "user", "content": text}
            ])
        responses.append(response.choices[0].message.content) #type: ignore

    text = "\n\n".join(responses) #type: ignore

    transcript_ = transcripts[0]
    if destination_path is None:
        destination_path = transcript_.text_path.parent / ("optimized_" + transcript_.text_path.name)
    else:
        destination_path = Path(destination_path) / ("optimized_" + transcript_.text_path.name)

    optimized_transcript = Transcript.to_file(text, destination_path)
    return optimized_transcript
