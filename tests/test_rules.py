from escoba.core.cards import Card, Suit
from escoba.core.deck import Deck
from escoba.core.game import Game
from escoba.core.player import Player
from escoba.core.rules import (
    card_value,
    end_turn,
    find_captures,
    play_card,
    score_round,
    start_round,
)


def make_player(captured, escobas=0):
    player = Player("p")
    player.captured = list(captured)
    player.escobas = escobas
    return player


def test_number_cards_keep_their_value():
    for rank in range(1, 8):
        assert card_value(Card(Suit.OROS, rank)) == rank


def test_face_card_values():
    assert card_value(Card(Suit.COPAS, 10)) == 8
    assert card_value(Card(Suit.COPAS, 11)) == 9
    assert card_value(Card(Suit.COPAS, 12)) == 10


def test_deck_values_cover_1_to_10():
    assert sorted({card_value(card) for card in Deck().cards}) == list(range(1, 11))


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


def test_score_no_players():
    assert score_round([]) == []


def test_score_one_point_per_escoba():
    players = [make_player([], escobas=3), make_player([], escobas=0)]
    assert score_round(players) == [3, 0]


def test_score_most_cards():
    players = [
        make_player([Card(Suit.COPAS, 1), Card(Suit.COPAS, 2)]),
        make_player([Card(Suit.BASTOS, 1)]),
    ]
    assert score_round(players) == [1, 0]


def test_score_most_cards_tied():
    players = [
        make_player([Card(Suit.COPAS, 1)]),
        make_player([Card(Suit.BASTOS, 1)]),
    ]
    assert score_round(players) == [0, 0]


def test_score_most_oros():
    # same number of cards, but player 1 has more oros
    players = [
        make_player([Card(Suit.OROS, 1), Card(Suit.OROS, 2)]),
        make_player([Card(Suit.OROS, 3), Card(Suit.COPAS, 1)]),
    ]
    assert score_round(players) == [1, 0]


def test_score_most_oros_tied():
    players = [
        make_player([Card(Suit.OROS, 1), Card(Suit.COPAS, 2)]),
        make_player([Card(Suit.OROS, 3), Card(Suit.COPAS, 1)]),
    ]
    assert score_round(players) == [0, 0]


def test_score_siete_de_velo():
    # player 1 gets velo + most oros + most sevens, player 2 nothing
    players = [
        make_player([Card(Suit.OROS, 7)]),
        make_player([Card(Suit.COPAS, 1)]),
    ]
    assert score_round(players) == [3, 0]


def test_score_most_sevens():
    players = [
        make_player([Card(Suit.COPAS, 7), Card(Suit.ESPADAS, 7)]),
        make_player([Card(Suit.BASTOS, 7), Card(Suit.BASTOS, 1)]),
    ]
    assert score_round(players) == [1, 0]


def test_score_most_sevens_tied():
    players = [
        make_player([Card(Suit.COPAS, 7), Card(Suit.COPAS, 1)]),
        make_player([Card(Suit.BASTOS, 7), Card(Suit.BASTOS, 1)]),
    ]
    assert score_round(players) == [0, 0]


def make_state(hand, table):
    # two players, the first one is up and holds `hand`
    you, cpu = Player("You"), Player("CPU", is_cpu=True)
    you.hand = list(hand)
    return Game([you, cpu], Deck(), list(table))


def test_play_without_capture_puts_card_on_table():
    played = Card(Suit.OROS, 2)
    state = make_state([played], [Card(Suit.COPAS, 3)])
    you = state.players[0]

    play_card(state, played)

    assert played in state.table
    assert you.hand == []
    assert you.captured == []
    assert state.turn == 1


def test_play_with_capture_takes_cards():
    played = Card(Suit.OROS, 5)
    rey = Card(Suit.COPAS, 12)
    three = Card(Suit.BASTOS, 3)
    state = make_state([played], [rey, three])
    you = state.players[0]

    play_card(state, played, [rey])

    assert state.table == [three]
    assert set(you.captured) == {played, rey}
    assert you.escobas == 0
    assert state.last_capturer is you
    assert state.turn == 1


def test_clearing_table_is_escoba():
    played = Card(Suit.OROS, 1)
    table = [Card(Suit.COPAS, 2), Card(Suit.ESPADAS, 4), Card(Suit.BASTOS, 10)]
    state = make_state([played], table)

    play_card(state, played, table)

    assert state.table == []
    assert state.players[0].escobas == 1


def test_end_turn_waits_while_cards_in_hand():
    state = make_state([Card(Suit.OROS, 1)], [])

    end_turn(state)

    assert len(state.players[0].hand) == 1
    assert len(state.players[1].hand) == 0
    assert len(state.deck) == 40


def test_end_turn_redeals_when_hands_empty():
    state = make_state([], [])

    end_turn(state)

    assert all(len(player.hand) == 3 for player in state.players)
    assert len(state.deck) == 34


def test_end_round_gives_table_to_last_capturer_and_scores():
    velo = Card(Suit.OROS, 7)
    leftover = Card(Suit.COPAS, 1)
    state = make_state([], [leftover])
    state.deck.cards = []
    you, cpu = state.players
    you.captured = [velo]
    state.last_capturer = you

    end_turn(state)

    assert state.table == []
    assert set(you.captured) == {velo, leftover}
    # most cards + most oros + most sevens + siete de velo
    assert state.scores == {you: 4, cpu: 0}


def test_start_round_resets_and_deals():
    state = make_state([], [])
    state.players[0].captured = [Card(Suit.OROS, 1)]
    state.players[0].escobas = 2

    start_round(state)

    assert len(state.table) == 4
    assert all(len(player.hand) == 3 for player in state.players)
    assert len(state.deck) == 30
    assert state.players[0].captured == []
    assert state.players[0].escobas == 0


def test_full_round_keeps_all_40_cards():
    state = make_state([], [])
    start_round(state)

    # everyone just plays their first card and takes the first capture they can
    while any(player.hand for player in state.players):
        player = state.get_current_player()
        card = player.hand[0]
        captures = find_captures(card, state.table)
        play_card(state, card, captures[0] if captures else ())
        end_turn(state)

    captured = sum(len(player.captured) for player in state.players)
    assert len(state.deck) == 0
    assert captured + len(state.table) == 40
    assert sum(state.scores.values()) > 0
