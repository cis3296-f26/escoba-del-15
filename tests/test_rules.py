from escoba.core.card import Card, Suit
from escoba.core.deck import Deck
from escoba.core.game import Game
from escoba.core.player import Player
from escoba.core.rules import (
    end_turn,
    find_captures,
    play_card,
    score_round,
    start_round,
)

def make_game(hand, table):
    # two players, the first one is up and holds `hand`
    you = Player(0, "You")
    cpu = Player(1, "CPU", is_cpu=True)
    game = Game([you, cpu])
    game.table = list(table)
    game.player_states[you.id].hand = list(hand)
    game.player_states[cpu.id].hand = []
    return game

def make_scored_game(captured_lists, escobas_list=None):
    players = [
        Player(i, f"p{i}")
        for i in range(len(captured_lists))
    ]
    game = Game(players)
    for i, captured in enumerate(captured_lists):
        game.player_states[i].captured = list(captured)
        if escobas_list is not None:
            game.player_states[i].escobas = escobas_list[i]
    return game

def test_number_cards_keep_their_value():
    for rank in range(1, 8):
        assert Card(Suit.OROS, rank).value == rank

def test_face_card_values():
    assert Card(Suit.COPAS, 10).value == 8
    assert Card(Suit.COPAS, 11).value == 9
    assert Card(Suit.COPAS, 12).value == 10

def test_deck_values_cover_1_to_10():
    assert sorted({card.value for card in Deck().cards}) == list(range(1, 11))

def test_no_captures_on_empty_table():
    assert find_captures(Card(Suit.OROS, 5), []) == []

def test_single_card_capture():
    played = Card(Suit.OROS, 5)
    rey = Card(Suit.COPAS, 12)
    assert find_captures(played, [rey, Card(Suit.BASTOS, 3)]) == [(rey,)]

def test_multiple_captures_are_all_returned():
    played = Card(Suit.OROS, 7)
    one = Card(Suit.COPAS, 1)
    seven = Card(Suit.ESPADAS, 7)
    three = Card(Suit.BASTOS, 3)
    five = Card(Suit.OROS, 5)
    sota = Card(Suit.COPAS, 10)

    captures = find_captures(played, [one, seven, three, five, sota])

    assert sorted(map(set, captures), key=len) == sorted(
        [{sota}, {one, seven}, {three, five}], key=len
    )

def test_capture_can_take_whole_table():
    played = Card(Suit.OROS, 1)
    table = [Card(Suit.COPAS, 2), Card(Suit.ESPADAS, 4), Card(Suit.BASTOS, 10)]
    assert find_captures(played, table) == [tuple(table)]

def test_no_capture_when_nothing_adds_up():
    played = Card(Suit.OROS, 1)
    table = [Card(Suit.COPAS, 2), Card(Suit.ESPADAS, 3)]
    assert find_captures(played, table) == []

def test_score_one_point_per_escoba():
    game = make_scored_game([[], []], escobas_list=[3, 0])
    assert score_round(game) == [3, 0]

def test_score_most_cards():
    game = make_scored_game([
        [Card(Suit.COPAS, 1), Card(Suit.COPAS, 2)],
        [Card(Suit.BASTOS, 1)],
    ])
    assert score_round(game) == [1, 0]

def test_score_most_cards_tied():
    game = make_scored_game([
        [Card(Suit.COPAS, 1)],
        [Card(Suit.BASTOS, 1)],
    ])
    assert score_round(game) == [0, 0]

def test_score_most_oros():
    # same number of cards, but player 1 has more oros
    game = make_scored_game([
        [Card(Suit.OROS, 1), Card(Suit.OROS, 2)],
        [Card(Suit.OROS, 3), Card(Suit.COPAS, 1)],
    ])
    assert score_round(game) == [1, 0]

def test_score_most_oros_tied():
    game = make_scored_game([
        [Card(Suit.OROS, 1), Card(Suit.COPAS, 2)],
        [Card(Suit.OROS, 3), Card(Suit.COPAS, 1)],
    ])
    assert score_round(game) == [0, 0]

def test_score_siete_de_velo():
    # player 1 gets velo + most oros + most sevens, player 2 nothing
    game = make_scored_game([
        [Card(Suit.OROS, 7)],
        [Card(Suit.COPAS, 1)],
    ])
    assert score_round(game) == [3, 0]

def test_score_most_sevens():
    game = make_scored_game([
        [Card(Suit.COPAS, 7), Card(Suit.ESPADAS, 7)],
        [Card(Suit.BASTOS, 7), Card(Suit.BASTOS, 1)],
    ])
    assert score_round(game) == [1, 0]

def test_score_most_sevens_tied():
    game = make_scored_game([
        [Card(Suit.COPAS, 7), Card(Suit.COPAS, 1)],
        [Card(Suit.BASTOS, 7), Card(Suit.BASTOS, 1)],
    ])
    assert score_round(game) == [0, 0]

def test_play_without_capture_puts_card_on_table():
    played = Card(Suit.OROS, 2)
    game = make_game([played], [Card(Suit.COPAS, 3)])
    you = game.players[0]

    play_card(game, played)

    assert played in game.table
    assert game.player_states[you.id].hand == []
    assert game.player_states[you.id].captured == []
    assert game.turn == 1

def test_play_with_capture_takes_cards():
    played = Card(Suit.OROS, 5)
    rey = Card(Suit.COPAS, 12)
    three = Card(Suit.BASTOS, 3)
    game = make_game([played], [rey, three])
    you = game.players[0]

    play_card(game, played, [rey])

    assert game.table == [three]
    assert set(game.player_states[you.id].captured) == {played, rey}
    assert game.player_states[you.id].escobas == 0
    assert game.last_capturer == you.id
    assert game.turn == 1

def test_clearing_table_is_escoba():
    played = Card(Suit.OROS, 1)
    table = [Card(Suit.COPAS, 2), Card(Suit.ESPADAS, 4), Card(Suit.BASTOS, 10)]
    game = make_game([played], table)
    you = game.players[0]

    play_card(game, played, table)

    assert game.table == []
    assert game.player_states[you.id].escobas == 1

def test_end_turn_waits_while_cards_in_hand():
    game = make_game([Card(Suit.OROS, 1)], [])
    you = game.players[0]
    cpu = game.players[1]

    end_turn(game)

    assert len(game.player_states[you.id].hand) == 1
    assert len(game.player_states[cpu.id].hand) == 0
    assert len(game.deck) == 40

def test_end_turn_redeals_when_hands_empty():
    game = make_game([], [])

    end_turn(game)

    assert all(
        len(game.player_states[player.id].hand) == 3
        for player in game.players
    )
    assert len(game.deck) == 34

def test_end_round_gives_table_to_last_capturer_and_scores():
    velo = Card(Suit.OROS, 7)
    leftover = Card(Suit.COPAS, 1)
    game = make_game([], [leftover])
    game.deck.cards = []
    you, cpu = game.players
    game.player_states[you.id].captured = [velo]
    game.last_capturer = you.id

    end_turn(game)

    assert game.table == []
    assert set(game.player_states[you.id].captured) == {velo, leftover}
    # most cards + most oros + most sevens + siete de velo
    assert game.player_states[you.id].score == 4
    assert game.player_states[cpu.id].score == 0

def test_start_round_resets_and_deals():
    game = make_game([], [])
    you = game.players[0]
    game.player_states[you.id].captured = [Card(Suit.OROS, 1)]
    game.player_states[you.id].escobas = 2

    start_round(game)

    assert len(game.table) == 4
    assert all(
        len(game.player_states[player.id].hand) == 3
        for player in game.players
    )
    assert len(game.deck) == 30
    assert game.player_states[you.id].captured == []
    assert game.player_states[you.id].escobas == 0

def test_full_round_keeps_all_40_cards():
    game = make_game([], [])
    start_round(game)

    # everyone just plays their first card and takes the first capture they can
    while any(game.player_states[player.id].hand for player in game.players):
        player_id = game.current_player_id
        state = game.player_states[player_id]
        card = state.hand[0]
        captures = find_captures(card, game.table)
        play_card(game, card, captures[0] if captures else ())
        end_turn(game)

    captured = sum(
        len(game.player_states[player.id].captured)
        for player in game.players
    )
    assert len(game.deck) == 0
    assert captured + len(game.table) == 40
    assert sum(
        game.player_states[player.id].score for player in game.players
    ) > 0
