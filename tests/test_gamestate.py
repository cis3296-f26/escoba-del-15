import pytest

from escoba.core.gamestate import GameState
from escoba.core.deck import Deck
from escoba.core.player import Player

def make_two_player_state():
    you = Player("You")
    cpu = Player("CPU", is_cpu=True)
    state = GameState([you, cpu], Deck(), [])
    return state, you, cpu


def test_gamestate_initialization():
    players = ["Player 1", "Player 2"]
    deck = Deck()
    table = []

    state = GameState(players, deck, table)

    assert state.players is players
    assert state.deck is deck
    assert state.table is table
    assert state.turn == 0


def test_next_turn():
    state = GameState(
        players=["Player 1", "Player 2"],
        deck=Deck(),
        table=[]
    )

    assert state.turn == 0

    state.next_turn()
    assert state.turn == 1

    state.next_turn()
    assert state.turn == 0


def test_scores_start_at_zero():
    state, you, cpu = make_two_player_state()
    assert state.scores == {you: 0, cpu: 0}


def test_add_round_scores_adds_points():
    state, you, cpu = make_two_player_state()
    state.add_round_scores({you: 3, cpu: 1})
    assert state.scores == {you: 3, cpu: 1}


def test_round_scores_accumulate():
    state, you, cpu = make_two_player_state()
    state.add_round_scores({you: 3, cpu: 1})
    state.add_round_scores({you: 2, cpu: 4})
    assert state.scores == {you: 5, cpu: 5}


def test_add_round_scores_only_changes_listed_players():
    state, you, cpu = make_two_player_state()
    state.add_round_scores({you: 2})
    assert state.scores == {you: 2, cpu: 0}


def test_no_winner_below_21():
    state, you, cpu = make_two_player_state()
    state.add_round_scores({you: 20, cpu: 15})
    assert state.winner() is None


def test_winner_at_exactly_21():
    state, you, cpu = make_two_player_state()
    state.add_round_scores({you: 21, cpu: 10})
    assert state.winner() is you


def test_winner_above_21():
    state, you, cpu = make_two_player_state()
    state.add_round_scores({you: 10, cpu: 24})
    assert state.winner() is cpu


def test_highest_wins_when_both_over_21():
    state, you, cpu = make_two_player_state()
    state.add_round_scores({you: 23, cpu: 21})
    assert state.winner() is you


def test_tie_over_21_has_no_winner():
    state, you, cpu = make_two_player_state()
    state.add_round_scores({you: 22, cpu: 22})
    assert state.winner() is None


def test_game_not_over_below_21():
    state, you, cpu = make_two_player_state()
    state.add_round_scores({you: 20, cpu: 18})
    assert state.is_game_over() is False


def test_game_over_when_someone_wins():
    state, you, cpu = make_two_player_state()
    state.add_round_scores({you: 21, cpu: 5})
    assert state.is_game_over() is True


def test_game_not_over_on_tie():
    state, you, cpu = make_two_player_state()
    state.add_round_scores({you: 21, cpu: 21})
    assert state.is_game_over() is False


def test_get_current_player_follows_turn():
    state, you, cpu = make_two_player_state()
    assert state.get_current_player() is you

    state.next_turn()
    assert state.get_current_player() is cpu

    state.next_turn()
    assert state.get_current_player() is you


def test_last_capturer_starts_none():
    state, you, cpu = make_two_player_state()
    assert state.last_capturer is None


def test_deal_gives_each_player_3_cards():
    state, you, cpu = make_two_player_state()
    state.deal_cards()
    assert len(you.hand) == 3
    assert len(cpu.hand) == 3


def test_deal_removes_cards_from_deck():
    state, you, cpu = make_two_player_state()
    state.deal_cards()
    # 40 cards minus 3 for each of the 2 players
    assert len(state.deck) == 34


def test_dealt_cards_are_not_in_deck():
    state, you, cpu = make_two_player_state()
    state.deal_cards()
    for card in you.hand + cpu.hand:
        assert card not in state.deck.cards


def test_deal_to_full_hand_raises():
    state, you, cpu = make_two_player_state()
    state.deal_cards()
    # hands are already full, so a second deal can't fit any more cards
    with pytest.raises(ValueError):
        state.deal_cards()


def test_deal_from_short_deck_raises():
    state, you, cpu = make_two_player_state()
    # 2 players need 6 cards, leave only 5 in the deck
    state.deck.cards = state.deck.cards[:5]
    with pytest.raises(IndexError):
        state.deal_cards()
