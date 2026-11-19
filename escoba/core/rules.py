from itertools import combinations

from escoba.core.card import Card, Suit, SIETE_DE_VELO
from escoba.core.deck import Deck
from escoba.core.game import Game, PlayerState
from escoba.core.result import GameResult, RoundBreakdown, RoundResult

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

def is_legal_capture(card: Card, capture, table: list[Card]) -> bool:
    # an empty capture just means placing the card on the table
    if not capture:
        return True
    return (
        all(taken in table for taken in capture)
        and card.value + sum(taken.value for taken in capture) == TARGET_SUM
    )

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

def new_game(players) -> Game:
    game = Game(players)
    start_round(game)
    return game

def end_turn(game: Game) -> GameResult | RoundResult | None:
    if any(state.hand for state in game.player_states.values()):
        return None

    if len(game.deck) > 0:
        deal_cards(game)
        return None

    return end_round(game)

def end_round(game: Game) -> GameResult | RoundResult:
    if game.last_capturer is not None:
        game.player_states[game.last_capturer].captured.extend(game.table)
        game.table = []

    breakdown = score_round_breakdown(game)
    for player, entry in zip(game.players, breakdown):
        game.player_states[player.id].score += entry.round_total

    finished = finish_game(game)
    if finished is not None:
        return finished

    totals = tuple(game.player_states[p.id].score for p in game.players)
    return RoundResult(breakdown=breakdown, totals=totals)

def award_most(points: list[int], counts: list[int]) -> None:
    best = max(counts, default=0)
    if best > 0 and counts.count(best) == 1:
        points[counts.index(best)] += 1

def score_round(game: Game) -> list[int]:
    return [entry.round_total for entry in score_round_breakdown(game)]

def score_round_breakdown(game: Game) -> tuple[RoundBreakdown, ...]:
    states = [game.player_states[p.id] for p in game.players]
    n = len(states)

    most_cards = [0] * n
    most_oros = [0] * n
    most_sevens = [0] * n
    award_most(most_cards, [len(s.captured) for s in states])
    award_most(most_oros, [
        sum(c.suit == Suit.OROS for c in s.captured) for s in states
    ])
    award_most(most_sevens, [
        sum(c.rank == 7 for c in s.captured) for s in states
    ])

    return tuple(
        RoundBreakdown(
            most_cards=most_cards[i],
            most_oros=most_oros[i],
            most_sevens=most_sevens[i],
            velo=int(SIETE_DE_VELO in state.captured),
            escobas=state.escobas
        )
        for i, state in enumerate(states)
    )

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
        scores=scores
    )