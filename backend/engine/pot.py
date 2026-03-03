"""Pot and side-pot handling."""
from __future__ import annotations

from typing import List, Tuple

from .table import Player


def build_side_pots(players: List[Player]) -> List[Tuple[int, List[Player]]]:
    """Construct main and side pots based on player contributions.

    Returns list of (pot_amount, eligible_players) ordered from main to side pots.
    """
    contributions = [(p, p.committed) for p in players if p.committed > 0]
    if not contributions:
        return []
    contributions.sort(key=lambda x: x[1])
    unique_levels = sorted({c[1] for c in contributions})
    pots: List[Tuple[int, List[Player]]] = []
    prev = 0
    for level in unique_levels:
        amount = (level - prev) * len([c for c in contributions if c[1] >= level])
        eligible = [c[0] for c in contributions if c[1] >= level and c[0].is_active]
        if amount > 0:
            pots.append((amount, eligible))
        prev = level
    return pots


def distribute_pots(pots: List[Tuple[int, List[Player]]], winners: List[List[Player]]) -> None:
    """Distribute each pot to corresponding winners list.

    winners[i] contains players tied for pot i.
    """
    for (amount, eligible), pot_winners in zip(pots, winners):
        share = amount // len(pot_winners)
        remainder = amount % len(pot_winners)
        for idx, player in enumerate(pot_winners):
            player.stack += share + (1 if idx < remainder else 0)
