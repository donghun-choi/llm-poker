import asyncio

import pytest

from backend.api.routes import game_manager, GameManager
from backend.api.schemas import GameSettings


@pytest.mark.asyncio
async def test_event_ordering():
    mgr = GameManager()
    game_id = mgr.create_game(GameSettings())
    stream = mgr.event_stream(game_id)
    events = []
    async for event in stream:
        events.append(event["type"])
        if len(events) >= 5:
            break
    assert events[:5] == ["new_hand", "deal", "your_turn", "showdown", "hand_result"]
