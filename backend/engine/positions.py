"""Position utilities for 6-max."""
from __future__ import annotations

POSITIONS = ["BTN", "SB", "BB", "UTG", "HJ", "CO"]


def rotate_button(current_button: int, seats: int = 6) -> int:
    """Return next button index for a 6-max table."""
    if seats <= 0:
        raise ValueError("seats must be positive")
    return (current_button + 1) % seats
