# simple greedy cpu opponent

from escoba.core.card import Card, Suit, SIETE_DE_VELO
from escoba.core.game import Game
from escoba.core.rules import find_captures

def move_priority(move, table: list[Card]):
    # tuples compare left to right, so earlier entries matter most
    card, capture = move
    taken = (card, *capture)
    return (
        len(capture) == len(table),  # escoba
        SIETE_DE_VELO in taken,
        sum(c.rank == 7 for c in taken),
        sum(c.suit == Suit.OROS for c in taken),
        len(taken),
    )

def choose_cpu_move(game: Game) -> tuple[Card, tuple[Card, ...]]:
    hand = game.player_states[game.current_player_id].hand
    moves = [
        (card, capture)
        for card in hand
        for capture in find_captures(card, game.table)
    ]

    # nothing to capture: get rid of the lowest card
    if not moves:
        return min(hand, key=lambda card: card.value), ()

    return max(moves, key=lambda move: move_priority(move, game.table))
