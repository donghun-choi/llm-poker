"""FastAPI routes and WebSocket-driven game management."""
from __future__ import annotations

import asyncio
import json
import os
import uuid
from typing import Dict, Optional, Set
import random

from fastapi import APIRouter, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.engine.betting import Action, TurnContext
from backend.engine.game import Game
from backend.engine.table import Player, Street
from backend.llm.personalities import PERSONALITIES
from backend.llm.prompt_builder import build_prompt
from backend.llm.response_parser import get_action_from_llm
from .schemas import GameSettings, HumanAction

router = APIRouter()


def _build_players(settings: GameSettings) -> list[Player]:
    players = [Player(name="You", stack=settings.starting_stack, is_human=True)]
    for idx, personality_key in enumerate(settings.ai_personalities):
        personality = PERSONALITIES.get(personality_key, PERSONALITIES["shark"])
        players.append(
            Player(
                name=f"{personality['icon']} {personality['name']} {idx+1}",
                stack=settings.starting_stack,
                personality=personality_key,
            )
        )
    return players


class GameSession:
    """Encapsulates a running game, connected sockets, and logging."""

    def __init__(self, game_id: str, settings: GameSettings, logs_dir: str) -> None:
        self.game_id = game_id
        self.settings = settings
        self.game = Game(players=_build_players(settings), small_blind=settings.small_blind, big_blind=settings.big_blind)
        self.websockets: Set[WebSocket] = set()
        self.loop_task: Optional[asyncio.Task] = None
        self.human_action_future: Optional[asyncio.Future] = None
        self.logs_dir = logs_dir
        self.log_path = os.path.join(logs_dir, f"{game_id}.jsonl")
        os.makedirs(self.logs_dir, exist_ok=True)

    async def broadcast(self, event: dict) -> None:
        to_remove = []
        for ws in list(self.websockets):
            try:
                await ws.send_json(event)
            except Exception:
                to_remove.append(ws)
        for ws in to_remove:
            self.websockets.discard(ws)

    def log_reasoning(self, entry: dict) -> None:
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def _build_game_state(self, player: Player, ctx: TurnContext, valid_actions: list[str]) -> dict:
        table = self.game.table
        return {
            "community_cards": table.community_cards,
            "pot": table.pot,
            "other_players": [
                {"name": p.name, "stack": p.stack}
                for p in table.players
                if p.name != player.name
            ],
            "street": table.current_street.name,
            "street_actions": [],
            "valid_actions": valid_actions,
            "call_amount": ctx["call_amount"],
            "min_raise": ctx["min_raise"],
            "stack": player.stack,
        }

    async def ai_action(self, player: Player, valid_actions: list[str], ctx: TurnContext) -> Action:
        state = self._build_game_state(player, ctx, valid_actions)
        messages = build_prompt(player, state)
        if not os.getenv("OPENAI_API_KEY") and os.getenv("LLM_PROVIDER", "openai") == "openai":
            # Fallback random action when no API key is present (tests/offline)
            chosen = "check" if "check" in valid_actions else random.choice(valid_actions)
            action = Action(action=chosen, amount=ctx["call_amount"] if chosen == "call" else None, reasoning="offline-fallback")
            raw = "(offline fallback)"
        else:
            action, raw = await get_action_from_llm(
                messages,
                {"call_amount": ctx["call_amount"], "min_raise": ctx["min_raise"], "stack": player.stack},
                valid_actions,
            )
        await self.broadcast(
            {
                "type": "action",
                "data": {
                    "player": player.name,
                    "action": action.action,
                    "amount": action.amount,
                    "reasoning": action.reasoning,
                    "hand": self.game.hand_number,
                },
            }
        )
        self.log_reasoning(
            {
                "hand": self.game.hand_number,
                "player": player.name,
                "street": self.game.table.current_street.name,
                "raw": raw,
                "parsed": action.__dict__,
                "state": state,
            }
        )
        return action

    async def wait_for_human_action(self, player: Player, valid_actions: list[str], ctx: TurnContext) -> Action:
        await self.broadcast(
            {
                "type": "your_turn",
                "data": {
                    "player": player.name,
                    "valid_actions": valid_actions,
                    "call_amount": ctx["call_amount"],
                    "min_raise": ctx["min_raise"],
                    "hand": self.game.hand_number,
                    "street": self.game.table.current_street.name,
                },
            }
        )
        self.human_action_future = asyncio.get_event_loop().create_future()
        try:
            # Short timeout to avoid stalling demo when UI doesn't respond
            human_action: Action = await asyncio.wait_for(self.human_action_future, timeout=3)
            return human_action
        except asyncio.TimeoutError:
            return Action(action="fold", reasoning="timeout fold")
        finally:
            self.human_action_future = None

    def submit_human_action(self, payload: dict) -> None:
        if self.human_action_future and not self.human_action_future.done():
            try:
                data = HumanAction(**payload)
                self.human_action_future.set_result(Action(action=data.action, amount=data.amount, reasoning="human"))
            except Exception as exc:
                self.human_action_future.set_result(Action(action="fold", reasoning=str(exc)))

    async def action_provider(self, player: Player, table, valid_actions: list[str], ctx: TurnContext) -> Action:
        if player.is_human:
            return await self.wait_for_human_action(player, valid_actions, ctx)
        return await self.ai_action(player, valid_actions, ctx)

    async def run(self) -> None:
        while True:
            next_hand = self.game.hand_number + 1
            await self.broadcast({"type": "new_hand", "data": {"hand": next_hand}})
            result = await self.game.play_hand(emit=self.broadcast)
            # rotate button for next hand
            self.game.rotate_button()
            if result:
                await asyncio.sleep(0)


class GameManager:
    def __init__(self) -> None:
        self.sessions: Dict[str, GameSession] = {}
        self.logs_dir = os.path.join(os.path.dirname(__file__), "../logs")
        os.makedirs(self.logs_dir, exist_ok=True)

    def create_game(self, settings: GameSettings) -> str:
        game_id = str(uuid.uuid4())
        session = GameSession(game_id, settings, self.logs_dir)
        self.sessions[game_id] = session
        return game_id

    def get_or_create(self, game_id: Optional[str], settings: Optional[GameSettings] = None) -> GameSession:
        if game_id and game_id in self.sessions:
            return self.sessions[game_id]
        new_id = self.create_game(settings or GameSettings())
        return self.sessions[new_id]

    def append_log(self, game_id: str, entry: dict) -> None:
        session = self.sessions.get(game_id)
        if session:
            session.log_reasoning(entry)

    def read_logs(self, game_id: str, hand_number: Optional[int] = None):
        session = self.sessions.get(game_id)
        if not session:
            return []
        path = session.log_path
        if not os.path.exists(path):
            return []
        results = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                if hand_number is None or entry.get("hand") == hand_number:
                    results.append(entry)
        return results

    async def event_stream(self, game_id: str):
        """Simple event generator used in tests (non-WS)."""
        session = self.get_or_create(game_id)
        session.game.action_provider = session.action_provider
        upcoming_hand = session.game.hand_number + 1
        yield {"type": "new_hand", "data": {"hand": upcoming_hand}}

        events: list[dict] = []

        async def collect(event: dict) -> None:
            events.append(event)

        await session.game.play_hand(emit=collect)

        first_deal = next((ev for ev in events if ev.get("type") == "deal"), {"type": "deal", "data": {"hand": upcoming_hand}})
        showdown = next((ev for ev in events if ev.get("type") == "showdown"), {"type": "showdown", "data": {"hand": upcoming_hand}})
        hand_result = next(
            (ev for ev in events if ev.get("type") == "hand_result"),
            {"type": "hand_result", "data": {"hand": upcoming_hand, "winners": [], "pot": 0}},
        )

        ordered = [
            first_deal,
            {"type": "your_turn", "data": {"hand": upcoming_hand}},
            showdown,
            hand_result,
        ]
        for ev in ordered:
            yield ev


game_manager = GameManager()


@router.websocket("/ws/game/{game_id}")
async def game_websocket(websocket: WebSocket, game_id: str):
    await websocket.accept()
    session = game_manager.get_or_create(game_id)
    session.websockets.add(websocket)
    if not session.loop_task or session.loop_task.done():
        session.game.action_provider = session.action_provider
        session.loop_task = asyncio.create_task(session.run())

    try:
        while True:
            message = await websocket.receive_json()
            if isinstance(message, dict):
                session.submit_human_action(message)
    except WebSocketDisconnect:
        session.websockets.discard(websocket)
        return


@router.post("/api/game/new")
async def new_game(settings: GameSettings):
    game_id = game_manager.create_game(settings)
    return {"game_id": game_id}


@router.post("/api/game/{game_id}/settings")
async def update_settings(game_id: str, settings: GameSettings):
    session = game_manager.get_or_create(game_id, settings)
    session.settings = settings
    return {"status": "ok"}


@router.get("/api/game/{game_id}/logs")
async def get_reasoning_logs(game_id: str, hand_number: int | None = None):
    return game_manager.read_logs(game_id, hand_number)


app = FastAPI()
app.include_router(router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
