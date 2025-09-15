#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
import os
from typing import Optional


_CONFIGURED = False


def configure_logging(level_str: Optional[str] = None) -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    # Precedence: explicit arg > env var > default
    level_name = level_str or os.environ.get("VOICEBRIEF_LOG_LEVEL", "INFO")
    level_name = str(level_name).upper()
    level = getattr(logging, level_name, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    _CONFIGURED = True

