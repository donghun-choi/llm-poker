"""Pydantic schemas for API."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel


class GameSettings(BaseModel):
    starting_stack: int = 2000
    small_blind: int = 10
    big_blind: int = 20
    ai_personalities: list[str] = ["rock", "shark", "maniac", "fish", "shark"]
    llm_provider: Literal["openai", "ollama"] = "openai"


class GameEvent(BaseModel):
    type: str
    data: dict


class HumanAction(BaseModel):
    action: Literal["fold", "check", "call", "raise"]
    amount: Optional[int] = None
