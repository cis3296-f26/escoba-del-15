from dataclasses import dataclass
from itertools import combinations

from escoba.cards import Card, Suit

TARGET_SUM = 15

# 10, 11, 12 count as 8, 9, 10
# temp: should eventually be a part of the Card class
FACE_CARD_VALUES = {10: 8, 11: 9, 12: 10}

# temp: this constant should eventually be in the Card Class
SIETE_DE_VELO = Card(Suit.OROS, 7)


def card_value(card: Card) -> int:
    return FACE_CARD_VALUES.get(card.rank, card.rank)


def find_captures(played: Card, table: list[Card]) -> list[tuple[Card, ...]]:
    needed = TARGET_SUM - card_value(played)

    captures = []

    # try every non-empty group of table cards
    for size in range(1, len(table) + 1):
        for group in combinations(table, size):
            if sum(card_value(card) for card in group) == needed:
                captures.append(group)

    return captures


# temporary : this will most likely be incorporated
#    into a player class in the future
@dataclass
class PlayerRound:
    captured: list[Card]
    escobas: int = 0


def award_most(points: list[int], counts: list[int]) -> None:
    # +1 to whoever has the most, nobody gets it on a tie (or if everyone has 0)
    best = max(counts, default=0)
    if best > 0 and counts.count(best) == 1:
        points[counts.index(best)] += 1


def score_round(players: list[PlayerRound]) -> list[int]:
    # one escoba = one point - initialize w escobas
    points = [player.escobas for player in players]

    # count each player's cards, oros, sevens
    # keep them in a list in the correct order
    card_counts = []
    oros_counts = []
    seven_counts = []

    for player in players:
        oros = 0
        sevens = 0

        for card in player.captured:
            if card.suit == Suit.OROS:
                oros += 1
            if card.rank == 7:
                sevens += 1

        card_counts.append(len(player.captured))
        oros_counts.append(oros)
        seven_counts.append(sevens)

    award_most(points, card_counts)
    award_most(points, oros_counts)
    award_most(points, seven_counts)

    for i, player in enumerate(players):
        if SIETE_DE_VELO in player.captured:
            points[i] += 1

    return points
