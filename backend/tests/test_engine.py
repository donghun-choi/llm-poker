import pytest
from treys import Card, Evaluator

from backend.engine.deck import Deck
from backend.engine.positions import rotate_button, POSITIONS
from backend.engine.pot import build_side_pots, distribute_pots
from backend.engine.table import Player
from backend.engine.hand_evaluator import evaluate
from backend.engine.game import Game


def test_deck_unique_cards():
    deck = Deck()
    dealt = deck.deal(52)
    assert len(dealt) == 52
    assert len(set(dealt)) == 52
    with pytest.raises(ValueError):
        deck.deal(1)


def test_position_rotation():
    btn = 0
    order = []
    for _ in range(6):
        order.append(btn)
        btn = rotate_button(btn)
    assert order == [0, 1, 2, 3, 4, 5]


def test_side_pot_distribution_three_player_all_in():
    p1 = Player("A", stack=0)
    p2 = Player("B", stack=0)
    p3 = Player("C", stack=0)
    p1.committed = 50
    p2.committed = 100
    p3.committed = 200
    pots = build_side_pots([p1, p2, p3])
    assert pots[0][0] == 150  # main: 3 players * 50
    assert pots[1][0] == 100  # side: 2 players * (100-50)
    assert pots[2][0] == 100  # side: 1 player * (200-100)
    # distribute with winners: p1 wins main, p2 wins second, p3 wins third
    distribute_pots(pots, [[p1], [p2], [p3]])
    assert p1.stack == 150
    assert p2.stack == 100
    assert p3.stack == 100


def test_treys_parity():
    evaluator = Evaluator()
    hole = [Card.new("As"), Card.new("Ad")]
    board = [Card.new("Ah"), Card.new("Kd"), Card.new("Kh"), Card.new("2c"), Card.new("3d")]
    assert evaluate(hole, board) == evaluator.evaluate(board, hole)


@pytest.mark.asyncio
async def test_random_simulation_runs_50_hands():
    players = [Player(name=f"P{i}", stack=1000) for i in range(6)]
    game = Game(players)
    for _ in range(50):
        result = await game.play_hand()
        assert result.pot >= 0
        game.rotate_button()
    assert True
