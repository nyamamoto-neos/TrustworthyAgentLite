"""Environment helpers for the trustworthy multi-agent workflow."""

from __future__ import annotations

import os
from typing import Dict

from dotenv import load_dotenv


def prepare_environment() -> None:
    """Load environment variables and remove conflicting keys."""
    load_dotenv(override=True)
    # The tutorial relies on Cleanlab's TLM API, so drop OpenAI key if present.
    os.environ.pop("OPENAI_API_KEY", None)


def environment_summary() -> Dict[str, str]:
    """Return a short summary for debugging environment configuration."""
    return {
        "LLM": os.environ.get("LLM", "Not set"),
        "CLEANLAB_TLM_API_KEY": "****" if os.environ.get("CLEANLAB_TLM_API_KEY") else "Not set",
    }


def ensure_data_directory(path: str = "data") -> str:
    """Ensure the CSV output directory exists and return its path."""
    os.makedirs(path, exist_ok=True)
    return path
