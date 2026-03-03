"""Betting round utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Awaitable

from .table import Player, Street, Table


class TurnContext(Dict[str, int]):
    """Context info passed into the action provider."""


@dataclass
class Action:
    """Represents a player decision."""

    action: str
    amount: Optional[int] = None
    reasoning: Optional[str] = None


ActionProvider = Callable[[Player, Table, List[str], TurnContext], Awaitable[Action]]


class BettingRound:
    """Manage a single betting round."""

    def __init__(
        self,
        table: Table,
        starting_index: int,
        action_provider: ActionProvider,
        street: Street,
    ) -> None:
        self.table = table
        self.starting_index = starting_index
        self.action_provider = action_provider
        self.street = street
        self.highest_bet = max(p.current_bet for p in table.players)
        self.last_raise_amount = table.big_blind
        self.acted_since_raise: set[int] = set()

    def min_raise_amount(self) -> int:
        return max(self.table.big_blind, self.last_raise_amount)

    def valid_actions(self, player: Player) -> List[str]:
        call_amount = max(self.highest_bet - player.current_bet, 0)
        actions = []
        if call_amount == 0:
            actions.extend(["check", "raise"] if player.stack > 0 else ["check"])
        else:
            actions.append("fold")
            actions.append("call")
            if player.stack > call_amount:
                actions.append("raise")
        return actions

    def apply_action(self, player: Player, action: Action) -> bool:
        """Apply action; return True if a raise occurred."""
        action_type = action.action
        call_amount = max(self.highest_bet - player.current_bet, 0)
        if action_type == "fold":
            player.is_active = False
            player.current_bet = 0
            return False
        if action_type == "check":
            return False
        if action_type == "call":
            to_put = min(call_amount, player.stack)
            player.stack -= to_put
            player.current_bet += to_put
            player.committed += to_put
            self.table.pot += to_put
            return False
        if action_type == "raise":
            min_raise = self.min_raise_amount()
            target_total = action.amount if action.amount is not None else call_amount + min_raise
            # enforce minimum
            target_total = max(target_total, self.highest_bet + min_raise)
            # cap at stack (all-in)
            target_total = min(target_total, player.current_bet + player.stack)
            needed = target_total - player.current_bet
            player.stack -= needed
            player.current_bet += needed
            player.committed += needed
            self.table.pot += needed
            self.last_raise_amount = target_total - self.highest_bet
            self.highest_bet = target_total
            self.acted_since_raise = set([self.table.players.index(player)])
            return True
        raise ValueError(f"Unknown action {action_type}")

    async def run(self) -> None:
        players = self.table.players
        idx = self.starting_index
        total_players = len(players)
        loop_guard = 0
        last_raise_idx: Optional[int] = None

        while True:
            loop_guard += 1
            if loop_guard > 200:
                break
            player = players[idx]
            if player.is_active and player.stack >= 0:
                valid = self.valid_actions(player)
                ctx = TurnContext(
                    call_amount=max(self.highest_bet - player.current_bet, 0),
                    min_raise=self.min_raise_amount(),
                    highest_bet=self.highest_bet,
                    pot=self.table.pot,
                )
                action = await self.action_provider(player, self.table, valid, ctx)
                raised = self.apply_action(player, action)
                if not raised:
                    self.acted_since_raise.add(idx)
                else:
                    last_raise_idx = idx
                # check end conditions
                active_indices = [i for i, p in enumerate(players) if p.is_active and (p.stack > 0 or p.current_bet > 0)]
                if len(active_indices) <= 1:
                    break
                all_matched = all(
                    (p.current_bet == self.highest_bet or p.stack == 0) and p.is_active
                    for p in players
                )
                if all_matched and len(self.acted_since_raise) >= len(active_indices):
                    break
            idx = (idx + 1) % total_players
            if last_raise_idx is not None and idx == last_raise_idx:
                # everyone had a chance after last raise
                if all(
                    (p.current_bet == self.highest_bet or p.stack == 0) and p.is_active
                    for p in players
                ):
                    break
