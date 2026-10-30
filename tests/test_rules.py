from escoba.core.cards import Card, Suit
from escoba.core.deck import Deck
from escoba.core.rules import PlayerRound, card_value, find_captures, score_round


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
    players = [PlayerRound([], escobas=3), PlayerRound([], escobas=0)]
    assert score_round(players) == [3, 0]


def test_score_most_cards():
    players = [
        PlayerRound([Card(Suit.COPAS, 1), Card(Suit.COPAS, 2)]),
        PlayerRound([Card(Suit.BASTOS, 1)]),
    ]
    assert score_round(players) == [1, 0]


def test_score_most_cards_tied():
    players = [
        PlayerRound([Card(Suit.COPAS, 1)]),
        PlayerRound([Card(Suit.BASTOS, 1)]),
    ]
    assert score_round(players) == [0, 0]


def test_score_most_oros():
    # same number of cards, but player 1 has more oros
    players = [
        PlayerRound([Card(Suit.OROS, 1), Card(Suit.OROS, 2)]),
        PlayerRound([Card(Suit.OROS, 3), Card(Suit.COPAS, 1)]),
    ]
    assert score_round(players) == [1, 0]


def test_score_most_oros_tied():
    players = [
        PlayerRound([Card(Suit.OROS, 1), Card(Suit.COPAS, 2)]),
        PlayerRound([Card(Suit.OROS, 3), Card(Suit.COPAS, 1)]),
    ]
    assert score_round(players) == [0, 0]


def test_score_siete_de_velo():
    # player 1 gets velo + most oros + most sevens, player 2 nothing
    players = [
        PlayerRound([Card(Suit.OROS, 7)]),
        PlayerRound([Card(Suit.COPAS, 1)]),
    ]
    assert score_round(players) == [3, 0]


def test_score_most_sevens():
    players = [
        PlayerRound([Card(Suit.COPAS, 7), Card(Suit.ESPADAS, 7)]),
        PlayerRound([Card(Suit.BASTOS, 7), Card(Suit.BASTOS, 1)]),
    ]
    assert score_round(players) == [1, 0]


def test_score_most_sevens_tied():
    players = [
        PlayerRound([Card(Suit.COPAS, 7), Card(Suit.COPAS, 1)]),
        PlayerRound([Card(Suit.BASTOS, 7), Card(Suit.BASTOS, 1)]),
    ]
    assert score_round(players) == [0, 0]
