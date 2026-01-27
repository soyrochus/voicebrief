#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voicebrief - Converts video / audio conversations to text and subsequently
provides a summary into a manageable report.
@copyright: Copyright © 2024 Iwan van der Kleijn
@license: MIT
"""

# from moviepy.editor import AudioFileClip
from typing import List
from openai import OpenAI, OpenAIError
from pathlib import Path
from dotenv import load_dotenv
import tiktoken
import os

from voicebrief.data import Transcript
import logging


def _get_client() -> OpenAI:
    """Create an OpenAI client on demand.

    Avoids importing credentials during module import so `--help` works cleanly.
    """
    # Load from .env if present
    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY not set. Set it in environment or .env file."
        )
    try:
        logging.getLogger("voicebrief.gptapi").debug("Initializing OpenAI client")
        return OpenAI(api_key=api_key)
    except OpenAIError as e:
        raise RuntimeError(f"Failed to initialize OpenAI client: {e}")


def _get_model() -> str:
    """Get the OpenAI model to use from environment variable.
    
    Reads from OPENAI_MODEL environment variable with fallback to gpt-4o.
    """
    load_dotenv()
    model = os.environ.get("OPENAI_MODEL", "gpt-4o")
    return model


def _get_encoding(model: str):
    """Get the tiktoken encoding for a model with fallback.
    
    If the model is not recognized by tiktoken, falls back to cl100k_base
    which is used by GPT-4, GPT-3.5-turbo, and newer models.
    """
    log = logging.getLogger("voicebrief.gptapi")
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        log.warning(
            "Model '%s' not recognized by tiktoken. Falling back to cl100k_base encoding "
            "(used by GPT-4 and newer models).", model
        )
        return tiktoken.get_encoding("cl100k_base")


def speech_to_text(audio_path):
    """Transcribe an audio file using OpenAI.

    Uses a binary file handle (not Path) to avoid request parsing errors.
    Tries Whisper first, then falls back to GPT-4o Mini Transcribe.
    """
    client = _get_client()
    audio_path = Path(audio_path)
    if not audio_path.exists() or audio_path.stat().st_size == 0:
        raise FileNotFoundError(f"Audio file not found or empty: {audio_path}")

    log = logging.getLogger("voicebrief.gptapi")
    size = audio_path.stat().st_size
    log.debug("Preparing transcription upload: %s (size=%d bytes)", audio_path, size)
    with audio_path.open("rb") as f:
        try:
            response = client.audio.transcriptions.create(
                model="whisper-1", file=f
            )
            log.debug("Transcribed with model=whisper-1")
        except Exception as e:
            # Retry with newer model if Whisper is unavailable/retired or on server error
            log.warning("Primary transcription failed (%s). Falling back to gpt-4o-mini-transcribe.", type(e).__name__)
            f.seek(0)
            response = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe", file=f
            )
            log.debug("Transcribed with model=gpt-4o-mini-transcribe (fallback)")
    return response.text


def summarize_text(text):
    client = _get_client()
    model = _get_model()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You must create a summary of the provided text. Be concise and to the point.",
            },
            {"role": "user", "content": text},
        ],
    )

    return response.choices[0].message.content


def transcribe_audio(audio_path: Path, destination_dir_path=None) -> Transcript:

    if destination_dir_path is None:
        destination_dir_path = audio_path.parent

    destination_path = Path(destination_dir_path) / ("transcription_" + audio_path.name)

    audio_path = Path(audio_path)

    text = speech_to_text(audio_path)
    transcription_path = destination_path.with_suffix(".txt")

    transcript = Transcript.to_file(text, transcription_path)
    print(f"Transcript written to: {transcript.text_path}")
    return transcript


def generate_markdown_transcript(
    transcripts: List[Transcript], destination_path: Path | None = None
) -> Transcript:
    """Generate a high-fidelity human-readable markdown transcript.
    
    Processes the transcript in chunks if necessary to ensure the best possible
    formatting and readability while preserving all content with maximum fidelity.
    """
    client = _get_client()
    model = _get_model()
    log = logging.getLogger("voicebrief.gptapi")
    enc = _get_encoding(model)
    
    text = ""
    total_tokens = 0
    responses = []
    
    for transcript in transcripts:
        tokens = enc.encode(transcript.text)
        if total_tokens + len(tokens) > 4000:
            # Process accumulated text
            log.debug("Processing markdown chunk (tokens=%d)", total_tokens)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a professional transcription formatter. Convert the provided 
transcript into a well-formatted, human-readable markdown document with the highest possible fidelity 
to the original content. 

Guidelines:
- Preserve ALL content - do not summarize or omit anything
- Format as proper markdown with appropriate headings, lists, and emphasis
- Organize content into logical sections with clear headings
- Use proper markdown syntax for better readability
- Correct obvious transcription errors while maintaining meaning
- Add appropriate paragraph breaks for readability
- Ensure smooth reading flow while staying faithful to the source""",
                    },
                    {"role": "user", "content": text},
                ],
            )
            responses.append(response.choices[0].message.content)  # type: ignore
            text = transcript.text
            total_tokens = len(tokens)
        else:
            text += transcript.text + " "
            total_tokens += len(tokens)

    # Process any remaining text
    if text:
        log.debug("Processing final markdown chunk (tokens=%d)", total_tokens)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": """You are a professional transcription formatter. Convert the provided 
transcript into a well-formatted, human-readable markdown document with the highest possible fidelity 
to the original content. 

Guidelines:
- Preserve ALL content - do not summarize or omit anything
- Format as proper markdown with appropriate headings, lists, and emphasis
- Organize content into logical sections with clear headings
- Use proper markdown syntax for better readability
- Correct obvious transcription errors while maintaining meaning
- Add appropriate paragraph breaks for readability
- Ensure smooth reading flow while staying faithful to the source""",
                },
                {"role": "user", "content": text},
            ],
        )
        responses.append(response.choices[0].message.content)  # type: ignore

    text = "\n\n---\n\n".join(responses)  # type: ignore
    
    transcript_ = transcripts[0]
    if destination_path is None:
        destination_path = transcript_.text_path.parent / (
            "full_md_" + transcript_.text_path.stem + ".md"
        )
    else:
        destination_path = Path(destination_path) / (
            "full_md_" + transcript_.text_path.stem + ".md"
        )

    markdown_transcript = Transcript.to_file(text, destination_path)
    log.info("Markdown transcript written to: %s", markdown_transcript.text_path)
    return markdown_transcript


def optimize_transcriptions(
    transcripts: List[Transcript], destination_path: Path | None = None
) -> Transcript:
    """Add the text of all transcript and then calculate the total token size of the text using the tiktoken library"""
    client = _get_client()
    model = _get_model()
    # To get the tokeniser corresponding to a specific model in the OpenAI API:
    enc = _get_encoding(model)
    text = ""
    total_tokens = 0
    responses = []
    for transcript in transcripts:
        tokens = enc.encode(transcript.text)
        if total_tokens + len(tokens) > 4000:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": """Please verify, optionally correct and organize 
the following text into a coherent and well-structured format with clear, distinct paragraphs. 
Each paragraph should have a logical flow and connection to the next, maintaining consistency and 
clarity throughout the text. Paragraphs should be delimted with an empty line.""",  # noqa: E501,
                    },
                    {"role": "user", "content": text},
                ],
            )
            responses.append(response.choices[0].message.content)  # type: ignore
            text = transcript.text
            total_tokens = len(tokens)
        else:
            text += transcript.text + " "
            total_tokens += len(tokens)

    if text:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": """Please verify, optionally correct and organize the following text into 
a coherent and well-structured format with clear, distinct paragraphs. Each paragraph should have a logical 
flow and connection to the next, maintaining consistency and clarity throughout the text. Paragraphs should 
be delimted with an empty line.""",  # noqa: E501,
                },
                {"role": "user", "content": text},
            ],
        )
        responses.append(response.choices[0].message.content)  # type: ignore

    text = "\n\n".join(responses)  # type: ignore

    transcript_ = transcripts[0]
    if destination_path is None:
        destination_path = transcript_.text_path.parent / (
            "optimized_" + transcript_.text_path.name
        )
    else:
        destination_path = Path(destination_path) / (
            "optimized_" + transcript_.text_path.name
        )

    optimized_transcript = Transcript.to_file(text, destination_path)
    return optimized_transcript
