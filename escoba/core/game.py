# mutable match state

from dataclasses import dataclass, field

from escoba.core.card import Card
from escoba.core.deck import Deck
from escoba.core.player import Player

@dataclass
class PlayerState:
    hand: list = field(default_factory=list)
    captured: list = field(default_factory=list)
    escobas: int = 0
    score: int = 0
    capture_count: int = 0

class Game:
    def __init__(self, players: list[Player] | tuple[Player, ...]):
        self.players = tuple(players)

        if len(self.players) not in (2, 3, 4):
            raise ValueError("A game requires 2, 3, or 4 players")

        if len({player.id for player in self.players}) != len(self.players):
            raise ValueError("Player IDs must be unique")

        self.player_states = { 
            player.id: PlayerState() for player in self.players 
            }

        self.turn = 0
        self.last_capturer: int | None = None

        self.deck = Deck().shuffle()
        self.table: list[Card] = []
        
    @property
    def current_player_id(self):
        return self.players[self.turn].id
