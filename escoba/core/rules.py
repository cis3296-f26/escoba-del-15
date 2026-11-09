from itertools import combinations

from escoba.core.card import Card, Suit, SIETE_DE_VELO
from escoba.core.deck import Deck
from escoba.core.game import Game, PlayerState
from escoba.core.result import GameResult

WINNING_SCORE = 21
TARGET_SUM = 15

def find_captures(played: Card, table: list[Card]) -> list[tuple[Card, ...]]:
    needed = TARGET_SUM - played.value
    captures = []

    for size in range(1, len(table) + 1):
        for group in combinations(table, size):
            if sum(card.value for card in group) == needed:
                captures.append(group)

    return captures

def deal_cards(game: Game) -> None:
    for _ in range(3):
        for player in game.players:
            game.player_states[player.id].hand.append(game.deck.draw())

def play_card(game: Game, card: Card, capture=()) -> None:
    # assumes the move is legal (capture should come from find_captures)
    state = game.player_states[game.current_player_id]
    state.hand.remove(card)

    if capture:
        for taken in capture:
            game.table.remove(taken)
        state.captured.extend((card, *capture))
        game.last_capturer = game.current_player_id

        if not game.table:
            state.escobas += 1
    else:
        game.table.append(card)

    game.turn = (game.turn + 1) % len(game.players)

def start_round(game: Game) -> None:
    game.deck = Deck().shuffle()
    game.table = [game.deck.draw() for _ in range(4)]
    game.last_capturer = None

    game.player_states = {
        player.id: PlayerState(score=game.player_states[player.id].score)
        for player in game.players
    }

    deal_cards(game)

def end_turn(game: Game) -> GameResult | None:
    if any(state.hand for state in game.player_states.values()):
        return None

    if len(game.deck) > 0:
        deal_cards(game)
        return None

    return end_round(game)

def end_round(game: Game) -> GameResult | None:
    if game.last_capturer is not None:
        game.player_states[game.last_capturer].captured.extend(game.table)
        game.table = []

    points = score_round(game)
    for player, earned in zip(game.players, points):
        game.player_states[player.id].score += earned

    return finish_game(game)

def award_most(points: list[int], counts: list[int]) -> None:
    best = max(counts, default=0)
    if best > 0 and counts.count(best) == 1:
        points[counts.index(best)] += 1

def score_round(game: Game) -> list[int]:
    states = [game.player_states[player.id] for player in game.players]
    points = [state.escobas for state in states]

    card_counts = []
    oros_counts = []
    seven_counts = []

    for state in states:
        card_counts.append(len(state.captured))
        oros_counts.append(sum(card.suit == Suit.OROS for card in state.captured))
        seven_counts.append(sum(card.rank == 7 for card in state.captured))

    award_most(points, card_counts)
    award_most(points, oros_counts)
    award_most(points, seven_counts)

    for i, state in enumerate(states):
        if SIETE_DE_VELO in state.captured:
            points[i] += 1

    return points

def finish_game(game: Game) -> GameResult | None:
    scores = tuple(
        (player.id, game.player_states[player.id].score) for player in game.players
    )
    best = max(score for _, score in scores)
    leaders = [player_id for player_id, score in scores if score == best]

    if best < WINNING_SCORE or len(leaders) != 1:
        return None

    return GameResult(
        players=game.players,
        winner_id=leaders[0],
        scores=scores,
    )