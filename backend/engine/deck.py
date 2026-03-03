"""Deck utilities built on treys."""
from __future__ import annotations

import random
from typing import List

from treys import Deck as TreysDeck


class Deck:
    """Standard 52-card deck."""

    def __init__(self) -> None:
        self.cards = TreysDeck.GetFullDeck()
        self.shuffle()

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def deal(self, n: int) -> List[int]:
        if n > len(self.cards):
            raise ValueError("Not enough cards to deal")
        dealt, self.cards = self.cards[:n], self.cards[n:]
        return dealt

    @property
    def remaining(self) -> int:
        return len(self.cards)
