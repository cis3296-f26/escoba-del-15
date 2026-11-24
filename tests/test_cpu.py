from escoba.core.card import Card, Suit
from escoba.core.cpu import choose_cpu_move
from escoba.core.game import Game
from escoba.core.player import Player
from escoba.core.result import GameResult, RoundResult
from escoba.core.rules import end_turn, play_card, start_round

def make_game(hand, table):
    # two players, the cpu is up and holds `hand`
    cpu = Player(0, "CPU", is_cpu=True)
    you = Player(1, "You")
    game = Game([cpu, you])
    game.table = list(table)
    game.player_states[cpu.id].hand = list(hand)
    return game

def test_cpu_prefers_escoba_over_velo():
    velo = Card(Suit.OROS, 7)
    five = Card(Suit.COPAS, 5)
    sota = Card(Suit.BASTOS, 10)
    two = Card(Suit.ESPADAS, 2)
    # velo + sota takes the velo, 5 + sota + 2 clears the table
    game = make_game([velo, five], [sota, two])

    card, capture = choose_cpu_move(game)

    assert card == five
    assert set(capture) == {sota, two}

def test_cpu_prefers_velo_over_more_cards():
    played = Card(Suit.COPAS, 1)
    velo = Card(Suit.OROS, 7)
    two = Card(Suit.COPAS, 2)
    three = Card(Suit.BASTOS, 3)
    four = Card(Suit.ESPADAS, 4)
    five = Card(Suit.BASTOS, 5)
    # needs 14: velo + 2 + 5 (3 cards) or 2 + 3 + 4 + 5 (4 cards)
    game = make_game([played], [velo, two, three, four, five])

    card, capture = choose_cpu_move(game)

    assert set(capture) == {velo, two, five}

def test_cpu_prefers_more_cards():
    played = Card(Suit.COPAS, 5)
    rey = Card(Suit.BASTOS, 12)
    four = Card(Suit.ESPADAS, 4)
    six = Card(Suit.BASTOS, 6)
    extra = Card(Suit.COPAS, 1)
    # rey alone or 4 + 6, nothing else differs
    game = make_game([played], [rey, four, six, extra])

    card, capture = choose_cpu_move(game)

    assert set(capture) == {four, six}

def test_cpu_discards_lowest_card_when_no_capture():
    low = Card(Suit.COPAS, 1)
    game = make_game([Card(Suit.BASTOS, 12), low, Card(Suit.ESPADAS, 5)], [])

    assert choose_cpu_move(game) == (low, ())

def test_cpu_vs_cpu_plays_a_full_game():
    players = [Player(0, "a", is_cpu=True), Player(1, "b", is_cpu=True)]
    game = Game(players)
    start_round(game)

    result = None
    while not isinstance(result, GameResult):
        play_card(game, *choose_cpu_move(game))
        result = end_turn(game)

        if isinstance(result, RoundResult):
            start_round(game)
            result = None

    assert dict(result.scores)[result.winner_id] >= 21
