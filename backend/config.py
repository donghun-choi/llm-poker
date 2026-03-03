"""LLM provider configuration helper."""
from __future__ import annotations

import os
from typing import Optional

from openai import OpenAI

PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()


def get_client(api_key: Optional[str] = None) -> OpenAI:
    """Return an OpenAI-compatible client for the configured provider."""
    if PROVIDER == "ollama":
        return OpenAI(api_key=api_key or "ollama", base_url="http://localhost:11434/v1")
    return OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))


def get_model() -> str:
    """Return the model name for the configured provider."""
    if PROVIDER == "ollama":
        return os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")
