from itertools import combinations

from escoba.core.cards import Card, Suit
from escoba.core.deck import Deck
from escoba.core.player import Player

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


def play_card(state, card: Card, capture=()) -> None:
    # current player plays a card, either capturing `capture` or leaving it on the table
    # assumes the move is legal (capture should come from find_captures)
    player = state.get_current_player()
    player.remove_card(card)

    if capture:
        for taken in capture:
            state.table.remove(taken)
        player.add_captured([card, *capture])
        state.last_capturer = player

        # clearing the table is an escoba
        if not state.table:
            player.escobas += 1
    else:
        state.table.append(card)

    state.next_turn()


def start_round(state) -> None:
    # fresh shuffled deck, 4 cards on the table, 3 to each player
    state.deck = Deck()
    state.deck.shuffle()
    state.table = [state.deck.draw() for _ in range(4)]
    state.last_capturer = None

    for player in state.players:
        player.captured = []
        player.escobas = 0

    state.deal_cards()


def end_turn(state) -> None:
    # call after every play_card
    # once all hands are empty, deal again or finish the round
    if any(player.hand for player in state.players):
        return

    if len(state.deck) > 0:
        state.deal_cards()
    else:
        end_round(state)


def end_round(state) -> None:
    # leftover table cards go to whoever captured last (doesn't count as an escoba)
    if state.last_capturer is not None:
        state.last_capturer.add_captured(state.table)
        state.table = []

    points = score_round(state.players)
    state.add_round_scores(dict(zip(state.players, points)))


def award_most(points: list[int], counts: list[int]) -> None:
    # +1 to whoever has the most, nobody gets it on a tie (or if everyone has 0)
    best = max(counts, default=0)
    if best > 0 and counts.count(best) == 1:
        points[counts.index(best)] += 1


def score_round(players: list[Player]) -> list[int]:
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
