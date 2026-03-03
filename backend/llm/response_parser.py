"""LLM response parsing with validation and retries."""
from __future__ import annotations

import json
import asyncio
import re
from json import JSONDecodeError
from typing import Any, Dict, List

from pydantic import BaseModel, ValidationError

from backend.config import get_client, get_model
from backend.engine.betting import Action


class ParsedAction(BaseModel):
    action: str
    amount: int | None = None
    reasoning: str | None = None


JSON_PATTERN = re.compile(r"\{.*\}", re.DOTALL)


def parse_json_response(raw: str) -> Dict[str, Any]:
    match = JSON_PATTERN.search(raw)
    if match:
        raw = match.group(0)
    return json.loads(raw)


def validate_action(parsed: Dict[str, Any], valid_actions: List[str], call_amount: int, min_raise: int, stack: int) -> Action:
    action_type = parsed.get("action", "fold")
    amount = parsed.get("amount")
    if action_type not in valid_actions:
        action_type = "fold"
    if action_type == "call":
        amount = min(call_amount, stack)
    if action_type == "raise":
        if amount is None:
            amount = call_amount + min_raise
        amount = max(amount, call_amount + min_raise)
        amount = min(amount, stack)
    return Action(action=action_type, amount=amount, reasoning=parsed.get("reasoning"))


async def get_action_from_llm(messages: List[dict], game_state: Dict[str, Any], valid_actions: List[str]) -> tuple[Action, str]:
    client = get_client()
    model = get_model()
    call_amount = game_state.get("call_amount", 0)
    min_raise = game_state.get("min_raise", 0)
    stack = game_state.get("stack", 0)
    for attempt in range(3):
        raw = ""
        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=200,
            )
            raw = response.choices[0].message.content
            parsed_dict = parse_json_response(raw)
            parsed = ParsedAction.model_validate(parsed_dict)
            return validate_action(parsed.dict(), valid_actions, call_amount, min_raise, stack), raw
        except (JSONDecodeError, ValidationError):
            continue
    return Action(action="fold", reasoning="(parse failure — auto fold)"), raw
