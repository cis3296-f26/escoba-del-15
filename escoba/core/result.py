# frozen end-of-match snapshot

from dataclasses import dataclass

from escoba.core.player import Player

@dataclass(frozen=True)
class GameResult:
    players: tuple[Player, ...]
    winner_id: int
    scores: tuple[tuple[int, int], ...]