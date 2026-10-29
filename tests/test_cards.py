from escoba.core.cards import Suit, new_deck


def test_deck_has_40_cards():
    assert len(new_deck()) == 40


def test_deck_cards_are_unique():
    deck = new_deck()
    assert len(set(deck)) == len(deck)


def test_deck_has_10_cards_per_suit():
    deck = new_deck()
    for suit in Suit:
        assert len([card for card in deck if card.suit == suit]) == 10

