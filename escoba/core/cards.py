
from enum import Enum
from dataclasses import dataclass


class Suit(Enum):
    OROS = "oros"
    COPAS = "copas"
    ESPADAS = "espadas"
    BASTOS = "bastos"


@dataclass(frozen=True)
class Card:
    suit: Suit
    rank: int


def new_deck():
    ranks = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12]

    deck = []

    for suit in Suit:
        for rank in ranks:
            deck.append(Card(suit, rank))

    return deck
