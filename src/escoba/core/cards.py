
from enum import Enum
from dataclasses import dataclass


class Suit(Enum):
    OROS = "oros"
    COPAS = "copas"
    ESPADAS = "espadas"
    BASTOS = "bastos"

RANKS = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12]


@dataclass(frozen=True)
class Card:
    suit: Suit
    rank: int