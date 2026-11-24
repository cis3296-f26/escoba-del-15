# frozen end-of-round / end-of-match snapshots

from dataclasses import dataclass

from escoba.core.player import Player

@dataclass(frozen=True)
class RoundBreakdown:
    most_cards: int = 0
    most_oros: int = 0
    most_sevens: int = 0
    velo: int = 0
    escobas: int = 0

    @property
    def round_total(self) -> int:
        return self.most_cards + self.most_oros + self.most_sevens + self.velo + self.escobas

@dataclass(frozen=True)
class RoundResult:
    # parallel to game.players
    breakdown: tuple[RoundBreakdown, ...]
    totals: tuple[int, ...]

@dataclass(frozen=True)
class GameResult:
    players: tuple[Player, ...]
    winner_id: int
    scores: tuple[tuple[int, int], ...]
