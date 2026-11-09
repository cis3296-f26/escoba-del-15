import pytest

from escoba.core.game import Game
from escoba.core.player import Player
from escoba.core.rules import deal_cards, finish_game

def make_two_player_game():
    you = Player(0, "You")
    cpu = Player(1, "CPU", is_cpu=True)
    game = Game([you, cpu])
    return game, you, cpu

def test_game_initialization():
    you = Player(0, "You")
    cpu = Player(1, "CPU", is_cpu=True)
    game = Game([you, cpu])

    assert game.players == (you, cpu)
    assert game.turn == 0
    assert game.table == []
    assert len(game.deck) == 40

def test_scores_start_at_zero():
    game, you, cpu = make_two_player_game()
    assert game.player_states[you.id].score == 0
    assert game.player_states[cpu.id].score == 0

def test_add_round_scores_adds_points():
    game, you, cpu = make_two_player_game()
    game.player_states[you.id].score += 3
    game.player_states[cpu.id].score += 1
    assert game.player_states[you.id].score == 3
    assert game.player_states[cpu.id].score == 1

def test_round_scores_accumulate():
    game, you, cpu = make_two_player_game()
    game.player_states[you.id].score += 3
    game.player_states[cpu.id].score += 1
    game.player_states[you.id].score += 2
    game.player_states[cpu.id].score += 4
    assert game.player_states[you.id].score == 5
    assert game.player_states[cpu.id].score == 5

def test_add_round_scores_only_changes_listed_players():
    game, you, cpu = make_two_player_game()
    game.player_states[you.id].score += 2
    assert game.player_states[you.id].score == 2
    assert game.player_states[cpu.id].score == 0

def test_no_winner_below_21():
    game, you, cpu = make_two_player_game()
    game.player_states[you.id].score = 20
    game.player_states[cpu.id].score = 15
    assert finish_game(game) is None

def test_winner_at_exactly_21():
    game, you, cpu = make_two_player_game()
    game.player_states[you.id].score = 21
    game.player_states[cpu.id].score = 10
    result = finish_game(game)
    assert result is not None
    assert result.winner_id == you.id

def test_winner_above_21():
    game, you, cpu = make_two_player_game()
    game.player_states[you.id].score = 10
    game.player_states[cpu.id].score = 24
    result = finish_game(game)
    assert result is not None
    assert result.winner_id == cpu.id

def test_highest_wins_when_both_over_21():
    game, you, cpu = make_two_player_game()
    game.player_states[you.id].score = 23
    game.player_states[cpu.id].score = 21
    result = finish_game(game)
    assert result is not None
    assert result.winner_id == you.id

def test_tie_over_21_has_no_winner():
    game, you, cpu = make_two_player_game()
    game.player_states[you.id].score = 22
    game.player_states[cpu.id].score = 22
    assert finish_game(game) is None

def test_game_not_over_below_21():
    game, you, cpu = make_two_player_game()
    game.player_states[you.id].score = 20
    game.player_states[cpu.id].score = 18
    assert finish_game(game) is None

def test_game_over_when_someone_wins():
    game, you, cpu = make_two_player_game()
    game.player_states[you.id].score = 21
    game.player_states[cpu.id].score = 5
    assert finish_game(game) is not None

def test_game_not_over_on_tie():
    game, you, cpu = make_two_player_game()
    game.player_states[you.id].score = 21
    game.player_states[cpu.id].score = 21
    assert finish_game(game) is None

def test_current_player_follows_turn():
    game, you, cpu = make_two_player_game()
    assert game.current_player_id == you.id

    game.turn = 1
    assert game.current_player_id == cpu.id

    game.turn = 0
    assert game.current_player_id == you.id

def test_last_capturer_starts_none():
    game, you, cpu = make_two_player_game()
    assert game.last_capturer is None

def test_deal_gives_each_player_3_cards():
    game, you, cpu = make_two_player_game()
    deal_cards(game)
    assert len(game.player_states[you.id].hand) == 3
    assert len(game.player_states[cpu.id].hand) == 3

def test_deal_removes_cards_from_deck():
    game, you, cpu = make_two_player_game()
    deal_cards(game)
    # 40 cards minus 3 for each of the 2 players
    assert len(game.deck) == 34

def test_dealt_cards_are_not_in_deck():
    game, you, cpu = make_two_player_game()
    deal_cards(game)
    for card in (
        game.player_states[you.id].hand
        + game.player_states[cpu.id].hand
    ):
        assert card not in game.deck.cards

def test_deal_from_short_deck_raises():
    game, you, cpu = make_two_player_game()
    # 2 players need 6 cards, leave only 5 in the deck
    game.deck.cards = game.deck.cards[:5]
    with pytest.raises(IndexError):
        deal_cards(game)
