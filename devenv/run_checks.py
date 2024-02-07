#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voicebrief - Converts video / audio conversations to text and subsequently provides a summary into a manageable report.
@copyright: Copyright © 2024 Iwan van der Kleijn
@license: MIT
"""

import subprocess


def run_checks():
    commands = [
        ["black", "voicebrief"],
        ["flake8", "voicebrief"],
        ["mypy", "voicebrief"],
        ["pytest"]
    ]

    for command in commands:
        result = subprocess.run(command)
        if result.returncode != 0:
            print(f"Command {command} failed with return code {result.returncode}")
            break  # Stop running the next commands if one fails

if __name__ == "__main__":
    run_checks()
