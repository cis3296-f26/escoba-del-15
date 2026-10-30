from escoba.cards import Card, Suit, new_deck
from escoba.rules import card_value, find_captures


def test_number_cards_keep_their_value():
    for rank in range(1, 8):
        assert card_value(Card(Suit.OROS, rank)) == rank


def test_face_card_values():
    assert card_value(Card(Suit.COPAS, 10)) == 8
    assert card_value(Card(Suit.COPAS, 11)) == 9
    assert card_value(Card(Suit.COPAS, 12)) == 10


def test_deck_values_cover_1_to_10():
    assert sorted({card_value(card) for card in new_deck()}) == list(range(1, 11))


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
