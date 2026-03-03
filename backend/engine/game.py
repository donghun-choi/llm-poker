"""Main game orchestrator."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Awaitable, Callable, List, Optional

from .betting import Action, BettingRound, TurnContext
from .deck import Deck
from .hand_evaluator import compare_hands
from .positions import POSITIONS, rotate_button
from .table import Player, Street, Table
from .pot import build_side_pots, distribute_pots

ActionProvider = Callable[[Player, Table, List[str], TurnContext], Awaitable[Action]]


@dataclass
class HandResult:
    winners: List[str]
    pot: int


class Game:
    """Simplified game engine for 6-max no-limit hold'em."""

    def __init__(
        self,
        players: List[Player],
        small_blind: int = 10,
        big_blind: int = 20,
        action_provider: Optional[ActionProvider] = None,
    ) -> None:
        self.table = Table(players=players, small_blind=small_blind, big_blind=big_blind)
        self.deck = Deck()
        self.action_provider = action_provider or self.random_action_provider
        self.hand_number = 0

    async def random_action_provider(
        self, player: Player, table: Table, valid: List[str], context: TurnContext
    ) -> Action:
        """Fallback action provider used in tests; picks a simple legal action."""
        if "check" in valid:
            return Action(action="check", reasoning="auto-check")
        if "call" in valid:
            return Action(action="call", reasoning="auto-call")
        return Action(action="fold", reasoning="auto-fold")

    def _assign_positions(self) -> None:
        for i, player in enumerate(self.table.players):
            player.position = POSITIONS[(i - self.table.button_position) % len(POSITIONS)]

    def post_blinds(self) -> None:
        sb_index = (self.table.button_position + 1) % len(self.table.players)
        bb_index = (self.table.button_position + 2) % len(self.table.players)
        players = self.table.players
        sb_player = players[sb_index]
        bb_player = players[bb_index]
        sb = min(self.table.small_blind, sb_player.stack)
        bb = min(self.table.big_blind, bb_player.stack)
        sb_player.stack -= sb
        bb_player.stack -= bb
        sb_player.current_bet = sb
        bb_player.current_bet = bb
        sb_player.committed += sb
        bb_player.committed += bb
        self.table.pot = sb + bb

    def deal_hole_cards(self) -> None:
        for player in self.table.players:
            if player.is_active:
                player.hole_cards = self.deck.deal(2)

    def deal_community(self, street: Street) -> None:
        if street == Street.FLOP:
            self.table.community_cards.extend(self.deck.deal(3))
        elif street in (Street.TURN, Street.RIVER):
            self.table.community_cards.extend(self.deck.deal(1))

    def first_to_act_index(self, street: Street) -> int:
        if street == Street.PREFLOP:
            return (self.table.button_position + 3) % len(self.table.players)
        return (self.table.button_position + 1) % len(self.table.players)

    async def run_betting_round(self, street: Street) -> None:
        for p in self.table.players:
            p.current_bet = 0
        start_idx = self.first_to_act_index(street)
        round_manager = BettingRound(self.table, start_idx, self.action_provider, street)
        await round_manager.run()

    def award_single_winner(self, winner: Player) -> HandResult:
        winner.stack += self.table.pot
        return HandResult(winners=[winner.name], pot=self.table.pot)

    def showdown(self) -> HandResult:
        active_players = [p for p in self.table.players if p.is_active]
        if len(active_players) == 1:
            return self.award_single_winner(active_players[0])
        pots = build_side_pots(self.table.players)
        winners_per_pot: List[List[Player]] = []
        for pot_amount, eligible in pots:
            contenders = [(p.name, p.hole_cards) for p in eligible]
            best_names = compare_hands(contenders, self.table.community_cards)
            pot_winners = [p for p in eligible if p.name in best_names]
            winners_per_pot.append(pot_winners)
        distribute_pots(pots, winners_per_pot)
        all_winners = list({p.name for group in winners_per_pot for p in group})
        return HandResult(winners=all_winners, pot=self.table.pot)

    async def play_hand(self, emit: Optional[Callable[[dict], Awaitable[None]]] = None) -> HandResult:
        self.hand_number += 1
        self.table.reset_for_new_hand()
        self.deck = Deck()
        self._assign_positions()
        self.post_blinds()
        self.deal_hole_cards()
        if emit:
            await emit(
                {
                    "type": "deal",
                    "data": {
                        "hand": self.hand_number,
                        "community_cards": [],
                    },
                }
            )

        for street in [Street.PREFLOP, Street.FLOP, Street.TURN, Street.RIVER]:
            self.table.current_street = street
            if street != Street.PREFLOP:
                self.deal_community(street)
                if emit:
                    await emit(
                        {
                            "type": "deal",
                            "data": {
                                "hand": self.hand_number,
                                "community_cards": self.table.community_cards,
                            },
                        }
                    )
            await self.run_betting_round(street)
            active = [p for p in self.table.players if p.is_active]
            if len(active) == 1:
                result = self.award_single_winner(active[0])
                if emit:
                    await emit(
                        {"type": "hand_result", "data": {"hand": self.hand_number, "winners": result.winners, "pot": result.pot}}
                    )
                return result
        result = self.showdown()
        if emit:
            await emit(
                {
                    "type": "showdown",
                    "data": {"hand": self.hand_number, "community_cards": self.table.community_cards},
                }
            )
            await emit(
                {"type": "hand_result", "data": {"hand": self.hand_number, "winners": result.winners, "pot": result.pot}}
            )
        return result

    def rotate_button(self) -> None:
        self.table.button_position = rotate_button(self.table.button_position, len(self.table.players))
