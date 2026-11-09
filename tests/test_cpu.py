from escoba.core.card import Card, Suit
from escoba.core.cpu import choose_cpu_move
from escoba.core.game import Game
from escoba.core.player import Player
from escoba.core.result import GameResult
from escoba.core.rules import end_turn, is_legal_capture, play_card, start_round

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

def test_legal_capture():
    table = [Card(Suit.COPAS, 2), Card(Suit.ESPADAS, 3)]
    # rey counts as 10
    assert is_legal_capture(Card(Suit.OROS, 12), table, table)

def test_illegal_capture_wrong_sum():
    table = [Card(Suit.COPAS, 2), Card(Suit.ESPADAS, 3)]
    assert not is_legal_capture(Card(Suit.OROS, 1), table, table)

def test_empty_capture_is_always_legal():
    assert is_legal_capture(Card(Suit.OROS, 1), (), [Card(Suit.COPAS, 2)])

def test_cpu_vs_cpu_plays_a_full_game():
    players = [Player(0, "a", is_cpu=True), Player(1, "b", is_cpu=True)]
    game = Game(players)
    start_round(game)

    result = None
    while result is None:
        play_card(game, *choose_cpu_move(game))
        result = end_turn(game)

        if result is None and not any(
            state.hand for state in game.player_states.values()
        ):
            start_round(game)

    assert isinstance(result, GameResult)
    assert dict(result.scores)[result.winner_id] >= 21
