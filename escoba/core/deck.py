# mutable 40-card deck

import random

from escoba.core.card import Card, ALL_CARDS

class Deck:
    def __init__(self):
        self.cards = list(ALL_CARDS)

    def shuffle(self, rng=random) -> Deck:
        rng.shuffle(self.cards)
        return self

    def draw(self) -> Card:
        return self.cards.pop()

    def __len__(self):
        return len(self.cards)