import random

import pygame
import pytest

from main import App
from escoba.core.card import Card, Suit, SIETE_DE_VELO
from escoba.core.player import Player
from escoba.core.result import GameResult
from escoba.core.rules import find_captures
from escoba.graphics.board import (
    EDGE_PADDING,
    HAND_SLOTS,
    TABLE_SLOTS,
    button_rect,
    row_lefts,
    table_layout,
)
from escoba.graphics.cards import CARD_WIDTH, CARD_HEIGHT
from escoba.screens import GameScreen, MenuScreen, ResultScreen, RoundOverScreen
from escoba.screens.game import CPU_MOVE

YOU = 0
CPU = 1

def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)

def click(pos):
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos)

def hand_card_pos(surface, index):
    width, height = surface.get_size()
    left = row_lefts(HAND_SLOTS, width // 2)[index]
    return (left + CARD_WIDTH // 2, height - EDGE_PADDING - CARD_HEIGHT // 2)

def table_card_pos(surface, index, count):
    x, y, max_width, _ = table_layout(surface)
    left = row_lefts(max(count, TABLE_SLOTS), x, max_width)[index]
    return (left + 5, y + CARD_HEIGHT // 2)

def press_button(app):
    app.screen.handle_event(click(button_rect(app.surface).center))

def set_cards(screen, hand, table, cpu_hand=None, deck=None):
    states = screen.game.player_states
    states[YOU].hand = list(hand)
    screen.game.table = list(table)
    if cpu_hand is not None:
        states[CPU].hand = list(cpu_hand)
    if deck is not None:
        screen.game.deck.cards = list(deck)

def play_last_card_of_round(app, screen):
    set_cards(screen, [Card(Suit.COPAS, 1)], [Card(Suit.BASTOS, 2)], cpu_hand=[], deck=[])
    screen.handle_event(key(pygame.K_1))
    press_button(app)

def show_result(app):
    players = (Player(YOU, "You"), Player(CPU, "CPU", is_cpu=True))
    result = GameResult(players=players, winner_id=YOU, scores=((YOU, 21), (CPU, 5)))
    app.change_screen(ResultScreen(app, result))

def colors_drawn(surface):
    width, height = surface.get_size()
    return {
        tuple(surface.get_at((x, y)))
        for x in range(0, width, 40)
        for y in range(0, height, 40)
    }

@pytest.fixture
def app():
    app = App()
    yield app
    pygame.quit()

@pytest.fixture
def game_screen(app):
    app.screen.handle_event(key(pygame.K_SPACE))
    return app.screen

def test_app_starts_on_menu(app):
    assert isinstance(app.screen, MenuScreen)

def test_space_on_menu_starts_game(app):
    app.screen.handle_event(key(pygame.K_SPACE))
    assert isinstance(app.screen, GameScreen)

def test_number_key_selects_hand_card(game_screen):
    game_screen.handle_event(key(pygame.K_2))
    assert game_screen.selected == 1
    assert len(game_screen.hand()) == 3

def test_clicking_hand_card_selects_and_deselects(app, game_screen):
    game_screen.handle_event(click(hand_card_pos(app.surface, 0)))
    assert game_screen.selected == 0

    game_screen.handle_event(click(hand_card_pos(app.surface, 0)))
    assert game_screen.selected is None

def test_clicking_table_card_toggles_highlight(app, game_screen):
    count = len(game_screen.game.table)

    game_screen.handle_event(click(table_card_pos(app.surface, 1, count)))
    assert game_screen.table_selected == {1}

    game_screen.handle_event(click(table_card_pos(app.surface, 1, count)))
    assert game_screen.table_selected == set()

def test_discard_puts_card_on_table(app, game_screen):
    played = Card(Suit.OROS, 1)
    set_cards(game_screen, [played, Card(Suit.COPAS, 2), Card(Suit.ESPADAS, 3)], [Card(Suit.BASTOS, 4)])

    game_screen.handle_event(key(pygame.K_1))
    press_button(app)

    assert played in game_screen.game.table
    assert played not in game_screen.hand()
    assert len(game_screen.game.player_states[YOU].hand) == 2
    assert game_screen.game.turn == CPU

def test_legal_capture_takes_cards(app, game_screen):
    five = Card(Suit.OROS, 5)
    rey = Card(Suit.COPAS, 12)
    three = Card(Suit.BASTOS, 3)
    set_cards(game_screen, [five, Card(Suit.COPAS, 1), Card(Suit.ESPADAS, 2)], [rey, three])

    game_screen.handle_event(key(pygame.K_1))
    game_screen.handle_event(click(table_card_pos(app.surface, 0, 2)))
    press_button(app)

    assert game_screen.game.table == [three]
    assert set(game_screen.game.player_states[YOU].captured) == {five, rey}
    assert game_screen.game.last_capturer == YOU

def test_illegal_capture_does_nothing(app, game_screen):
    hand = [Card(Suit.OROS, 5), Card(Suit.COPAS, 1), Card(Suit.ESPADAS, 2)]
    table = [Card(Suit.COPAS, 2), Card(Suit.BASTOS, 3)]
    set_cards(game_screen, hand, table)

    game_screen.handle_event(key(pygame.K_1))
    game_screen.handle_event(click(table_card_pos(app.surface, 0, 2)))
    press_button(app)

    assert game_screen.hand() == hand
    assert game_screen.game.table == table
    assert game_screen.game.turn == YOU

def test_input_ignored_on_cpu_turn(app, game_screen):
    game_screen.game.turn = CPU

    game_screen.handle_event(key(pygame.K_1))
    game_screen.handle_event(click(hand_card_pos(app.surface, 0)))

    assert game_screen.selected is None

def test_cpu_move_plays_one_cpu_card(game_screen):
    game_screen.game.turn = CPU

    game_screen.handle_event(pygame.event.Event(CPU_MOVE))

    assert len(game_screen.game.player_states[CPU].hand) == 2
    assert game_screen.game.turn == YOU

def test_round_end_shows_round_over_screen(app, game_screen):
    play_last_card_of_round(app, game_screen)
    assert isinstance(app.screen, RoundOverScreen)

def test_enter_continues_same_game_and_keeps_scores(app, game_screen):
    game_screen.game.player_states[YOU].score = 5
    game_screen.game.player_states[CPU].score = 3
    play_last_card_of_round(app, game_screen)
    assert isinstance(app.screen, RoundOverScreen)

    app.screen.handle_event(key(pygame.K_RETURN))

    assert app.screen is game_screen
    assert game_screen.game.player_states[YOU].score == 5
    assert game_screen.game.player_states[CPU].score == 3
    assert all(len(state.hand) == 3 for state in game_screen.game.player_states.values())
    assert len(game_screen.game.table) == 4

def test_other_keys_stay_on_round_over(app, game_screen):
    play_last_card_of_round(app, game_screen)
    round_over = app.screen
    assert isinstance(round_over, RoundOverScreen)

    app.screen.handle_event(key(pygame.K_SPACE))

    assert app.screen is round_over

def test_space_on_result_starts_new_game(app):
    show_result(app)

    app.screen.handle_event(key(pygame.K_SPACE))

    assert isinstance(app.screen, GameScreen)
    assert all(state.score == 0 for state in app.screen.game.player_states.values())

def test_n_on_result_returns_to_menu(app):
    show_result(app)

    app.screen.handle_event(key(pygame.K_n))

    assert isinstance(app.screen, MenuScreen)

def test_button_does_nothing_without_selection(app, game_screen):
    hand = list(game_screen.hand())
    table = list(game_screen.game.table)

    press_button(app)

    assert game_screen.hand() == hand
    assert game_screen.game.table == table
    assert game_screen.game.turn == YOU

def test_reaching_21_shows_result_screen(app, game_screen):
    game_screen.game.player_states[YOU].score = 20
    game_screen.game.player_states[YOU].captured = [SIETE_DE_VELO]

    play_last_card_of_round(app, game_screen)

    assert isinstance(app.screen, ResultScreen)
    assert app.screen.result.winner_id == YOU
    assert dict(app.screen.result.scores)[YOU] == 24

def test_full_game_reaches_result_screen(app):
    random.seed(0)
    app.screen.handle_event(key(pygame.K_SPACE))

    for _ in range(2000):
        screen = app.screen
        if isinstance(screen, ResultScreen):
            break

        if isinstance(screen, RoundOverScreen):
            screen.handle_event(key(pygame.K_RETURN))
        elif screen.is_cpu_turn():
            screen.handle_event(pygame.event.Event(CPU_MOVE))
        else:
            table = screen.game.table
            captures = find_captures(screen.hand()[0], table)
            screen.handle_event(key(pygame.K_1))
            for card in captures[0] if captures else ():
                screen.handle_event(click(table_card_pos(app.surface, table.index(card), len(table))))
            press_button(app)

    assert isinstance(app.screen, ResultScreen)
    assert max(score for _, score in app.screen.result.scores) >= 21

def test_closing_window_exits_cleanly(app):
    pygame.event.post(pygame.event.Event(pygame.QUIT))
    app.run()

def test_every_screen_draws_something(app, game_screen):
    game_screen.draw(app.surface)
    assert len(colors_drawn(app.surface)) > 1

    play_last_card_of_round(app, game_screen)
    assert isinstance(app.screen, RoundOverScreen)
    app.screen.draw(app.surface)
    assert len(colors_drawn(app.surface)) > 1

    show_result(app)
    app.screen.draw(app.surface)
    assert len(colors_drawn(app.surface)) > 1

    app.change_screen(MenuScreen(app, game_screen.game.players))
    app.screen.draw(app.surface)
    assert len(colors_drawn(app.surface)) > 1
