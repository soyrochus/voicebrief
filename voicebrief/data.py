#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voicebrief - Converts video / audio conversations to text and subsequently provides a summary into a manageable report.
@copyright: Copyright © 2024 Iwan van der Kleijn
@license: MIT
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Transcript:
    text: str
    text_path: Path

    @classmethod
    def to_file(cls, text: str, path: Path) -> "Transcript":
        path.write_text(text)
        return Transcript(text, path)
