"""Player stat tracking."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class PlayerStats:
    hands_played: int = 0
    vpip_count: int = 0
    pfr_count: int = 0
    three_bet_count: int = 0
    three_bet_opportunity: int = 0
    cbet_count: int = 0
    cbet_opportunity: int = 0
    cbet_fold_count: int = 0
    cbet_fold_opportunity: int = 0
    showdown_hands: List[str] = field(default_factory=list)

    @property
    def vpip(self) -> float:
        return self.vpip_count / max(self.hands_played, 1)

    @property
    def pfr(self) -> float:
        return self.pfr_count / max(self.hands_played, 1)

    @property
    def three_bet(self) -> float:
        return self.three_bet_count / max(self.three_bet_opportunity, 1)

    @property
    def cbet(self) -> float:
        return self.cbet_count / max(self.cbet_opportunity, 1)

    @property
    def cbet_fold(self) -> float:
        return self.cbet_fold_count / max(self.cbet_fold_opportunity, 1)


def update_stats(stats: PlayerStats, vpip: bool = False, pfr: bool = False) -> None:
    stats.hands_played += 1
    if vpip:
        stats.vpip_count += 1
    if pfr:
        stats.pfr_count += 1
