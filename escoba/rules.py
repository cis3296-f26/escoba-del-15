from itertools import combinations

from escoba.cards import Card

TARGET_SUM = 15

# 10, 11, 12 count as 8, 9, 10
FACE_CARD_VALUES = {10: 8, 11: 9, 12: 10}


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
