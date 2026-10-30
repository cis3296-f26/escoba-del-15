import random
import pytest

from escoba.core.cards import Card
from escoba.core.deck import Deck


def test_draw_returns_a_card_and_removes_it():
    deck = Deck()
    card = deck.draw()

    assert isinstance(card, Card)
    assert len(deck) == 39
    assert card not in deck.cards


def test_drawing_every_Card_gives_40_unique_Cards():
    deck = Deck()
    drawn = [deck.draw() for _ in range(40)]
    assert len(set(drawn)) == 40
    assert len(deck) == 0


def test_draw_from_empty_deck_raises_error():
    deck = Deck()
    for _ in range(40):
        deck.draw()
    with pytest.raises(IndexError):
        deck.draw()


def test_shuffle_keeps_the_same_cards():
    deck = Deck()
    before = set(deck.cards)
    deck.shuffle()
    assert set(deck.cards) == before
    assert len(deck) == 40


def test_shuffle_changes_the_order():
    deck = Deck()
    before = list(deck.cards)
    deck.shuffle(random.Random(42))
    assert deck.cards != before


def test_same_seed_gives_Same_order():
    first = Deck()
    second = Deck()
    first.shuffle(random.Random(42))
    second.shuffle(random.Random(42))
    assert first.cards == second.cards