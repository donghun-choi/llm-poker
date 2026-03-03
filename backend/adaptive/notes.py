"""Opponent note generation."""
from __future__ import annotations

from .tracker import PlayerStats


def estimate_style(stats: PlayerStats) -> str:
    if stats.vpip < 0.15:
        return "Nit"
    if stats.vpip < 0.30 and stats.pfr < 0.20:
        return "TAG"
    if stats.vpip >= 0.45 and stats.pfr >= 0.25:
        return "LAG"
    return "Fish"


def generate_opponent_notes(stats: PlayerStats, player_name: str) -> str:
    if stats.hands_played < 5:
        return f"{player_name}: Insufficient data (only {stats.hands_played} hands)"
    return (
        f"[{player_name}] Stats ({stats.hands_played} hands):\n"
        f"- VPIP: {stats.vpip:.0%} | PFR: {stats.pfr:.0%}\n"
        f"- 3bet: {stats.three_bet:.0%}\n"
        f"- C-bet: {stats.cbet:.0%} | C-bet fold: {stats.cbet_fold:.0%}\n"
        f"- Showdown hands: {stats.showdown_hands[-5:]}\n"
        f"- Estimated style: {estimate_style(stats)}\n"
        "→ Use this information to exploit this opponent."
    )
