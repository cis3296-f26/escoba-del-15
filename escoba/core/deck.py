import random

from escoba.core.cards import Card, Suit, RANKS


class Deck:
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in Suit for rank in RANKS]

    def shuffle(self, rng=random):
        rng.shuffle(self.cards)

    def draw(self) -> Card:
        if not self.cards:
            raise IndexError("You cannot draw from an empty deck")
        return self.cards.pop()

    def __len__(self):
        return len(self.cards)