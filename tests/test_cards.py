from escoba.core.cards import Suit
from escoba.core.deck import Deck


def test_deck_has_40_cards():
    assert len(Deck().cards) == 40


def test_deck_cards_are_unique():
    deck = Deck().cards
    assert len(set(deck)) == len(deck)


def test_deck_has_10_cards_per_suit():
    deck = Deck().cards
    for suit in Suit:
        assert len([card for card in deck if card.suit == suit]) == 10
