# frozen Spanish-deck cards
# face ranks 10/11/12 score as 8/9/10

from enum import Enum
from dataclasses import dataclass

class Suit(Enum):
    OROS = "oros"
    COPAS = "copas"
    ESPADAS = "espadas"
    BASTOS = "bastos"

RANKS = (1, 2, 3, 4, 5, 6, 7, 10, 11, 12)

@dataclass(frozen=True)
class Card:
    suit: Suit
    rank: int

    @property
    def value(self) -> int:
        return self.rank - 2 if self.rank >= 10 else self.rank

ALL_CARDS = tuple(
    Card(suit, rank)
    for suit in Suit
    for rank in RANKS
)

SIETE_DE_VELO = Card(Suit.OROS, 7)