"""LLM client factory."""
from __future__ import annotations

from backend.config import get_client


def make_client():
    return get_client()
