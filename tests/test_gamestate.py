
from escoba.core.gamestate import GameState
from escoba.core.cards import new_deck


def test_gamestate_initialization():
    players = ["Player 1", "Player 2"]
    deck = new_deck()
    table = []

    state = GameState(players, deck, table)

    assert state.players is players
    assert state.deck is deck
    assert state.table is table
    assert state.turn == 0
   


def test_next_turn():
    state = GameState(
        players=["Player 1", "Player 2"],
        deck=new_deck(),
        table=[]
    )

    assert state.turn == 0

    state.next_turn()
    assert state.turn == 1

    state.next_turn()
    assert state.turn == 0
