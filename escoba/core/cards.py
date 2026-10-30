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

RANKS = (1, 2, 3, 4, 5, 6, 7, 10, 11, 12)

ALL_CARDS = tuple(
    Card(suit, rank)
    for suit in Suit
    for rank in RANKS
    )

def new_deck():
    return list(ALL_CARDS)
