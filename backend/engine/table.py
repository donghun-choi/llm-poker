"""Table and player models."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional


class Street(Enum):
    PREFLOP = auto()
    FLOP = auto()
    TURN = auto()
    RIVER = auto()
    SHOWDOWN = auto()


@dataclass
class Player:
    name: str
    stack: int
    hole_cards: List[int] = field(default_factory=list)
    is_active: bool = True
    is_human: bool = False
    personality: Optional[str] = None
    current_bet: int = 0
    position: Optional[str] = None
    committed: int = 0  # total chips committed this hand

    def reset_for_hand(self) -> None:
        self.hole_cards = []
        self.is_active = self.stack > 0
        self.current_bet = 0
        self.committed = 0


@dataclass
class Table:
    players: List[Player]
    community_cards: List[int] = field(default_factory=list)
    pot: int = 0
    current_street: Street = Street.PREFLOP
    button_position: int = 0
    small_blind: int = 10
    big_blind: int = 20

    def reset_for_new_hand(self) -> None:
        self.community_cards = []
        self.pot = 0
        self.current_street = Street.PREFLOP
        for player in self.players:
            player.reset_for_hand()
