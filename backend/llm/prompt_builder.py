"""Prompt builder for LLM actions."""
from __future__ import annotations

from typing import List, Optional

from treys import Card

from .personalities import PERSONALITIES


def format_cards(cards: List[int]) -> str:
    if not cards:
        return "(none)"
    return " ".join(Card.int_to_pretty_str(c) for c in cards)


def format_stacks(players: List[dict]) -> str:
    return ", ".join(f"{p['name']}: ${p['stack']}" for p in players)


def format_actions(actions: List[str]) -> str:
    return ", ".join(actions) if actions else "(no actions yet)"


def format_valid_actions(valid: List[str]) -> str:
    return ", ".join(valid)


def get_personality_prompt(personality: str) -> str:
    return PERSONALITIES.get(personality, PERSONALITIES["shark"])["system_prompt"]


def build_prompt(player, game_state, opponent_notes: Optional[str] = None) -> List[dict]:
    system_msg = get_personality_prompt(player.personality)
    if opponent_notes:
        system_msg += f"\n\n## Opponent Analysis Notes\n{opponent_notes}"

    user_msg = f"""Current game situation:
- My hand: {format_cards(player.hole_cards)}
- Board: {format_cards(game_state['community_cards'])}
- Pot: ${game_state['pot']}
- My stack: ${player.stack}
- Opponent stacks: {format_stacks(game_state['other_players'])}
- Position: {player.position}
- Current street: {game_state['street']}
- This street's actions: {format_actions(game_state['street_actions'])}
- Valid actions: {format_valid_actions(game_state['valid_actions'])}

Respond ONLY in JSON:
{{"action": "fold|check|call|raise", "amount": <number only if raise>, "reasoning": "<brief explanation, max 50 chars>"}}"""

    return [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg},
    ]
