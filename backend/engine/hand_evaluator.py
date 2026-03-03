"""Hand evaluation helpers using treys."""
from __future__ import annotations

from typing import List, Tuple

from treys import Evaluator

_evaluator = Evaluator()


def evaluate(hole_cards: List[int], community_cards: List[int]) -> int:
    """Return treys rank (lower is better)."""
    return _evaluator.evaluate(community_cards, hole_cards)


def compare_hands(players_hole: List[Tuple[str, List[int]]], community_cards: List[int]) -> List[str]:
    """Return list of player names that tie for best hand."""
    scores = []
    for name, cards in players_hole:
        scores.append((name, evaluate(cards, community_cards)))
    scores.sort(key=lambda x: x[1])
    best = scores[0][1]
    winners = [name for name, score in scores if score == best]
    return winners
