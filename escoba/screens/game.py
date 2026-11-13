import pygame

from escoba.core.cpu import choose_cpu_move
from escoba.core.game import Game
from escoba.core.result import GameResult
from escoba.core.rules import end_turn, is_legal_capture, play_card, start_round
from escoba.graphics import render
from escoba.graphics.board import button_rect, hand_card_at, table_card_at
from escoba.screens.round_over import RoundOverScreen
from escoba.screens.screen import Screen

# how long the cpu "thinks" before playing
CPU_DELAY_MS = 800

# posted once CPU_DELAY_MS has passed on the cpu's turn
CPU_MOVE = pygame.event.custom_type()

def new_game(players):
    game = Game(players)
    start_round(game)
    return game

def take_turn(game, card, capture):
    # play a card, then deal / end the round / end the game as needed
    play_card(game, card, capture)
    result = end_turn(game)
    if result is not None:
        return result
    return game

def button_state(game, selected, table_selected):
    # (label, capture or None when disabled) for the discard/capture button
    if game.players[game.turn].is_cpu or selected is None:
        return "Discard", None

    card = game.player_states[game.current_player_id].hand[selected]
    capture = tuple(game.table[i] for i in sorted(table_selected))

    if not capture:
        return "Discard", ()
    if is_legal_capture(card, capture, game.table):
        return "Capture", capture
    return "Capture", None


class GameScreen(Screen):
    def __init__(self, app, players):
        self.app = app
        self.game = new_game(players)
        self.selected = None  # index of the selected card in your hand
        self.table_selected = set()  # indices of highlighted table cards
        self.schedule_cpu()

    def schedule_cpu(self):
        # the cpu plays when CPU_MOVE arrives, after a short pause
        if self.is_cpu_turn():
            pygame.time.set_timer(CPU_MOVE, CPU_DELAY_MS, loops=1)

    def is_cpu_turn(self):
        return self.game.players[self.game.turn].is_cpu

    def hand(self):
        return self.game.player_states[self.game.current_player_id].hand

    def play(self, card, capture):
        self.selected = None
        self.table_selected = set()
        state = take_turn(self.game, card, capture)
        if isinstance(state, GameResult):
            # imported here because the result screen imports this module
            from escoba.screens.result import ResultScreen
            self.app.change_screen(ResultScreen(self.app, state))
        elif not any(s.hand for s in self.game.player_states.values()):
            self.app.change_screen(RoundOverScreen(self.app, self))
        else:
            self.schedule_cpu()

    def handle_event(self, event):
        if self.is_cpu_turn():
            if event.type == CPU_MOVE:
                self.play(*choose_cpu_move(self.game))
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # select cards by clicking; only the button makes a move
            surface = self.app.surface
            hand = self.hand()
            index = hand_card_at(surface, event.pos)
            table_index = table_card_at(surface, event.pos, len(self.game.table))

            # the button plays the selected card as a discard or capture
            if button_rect(surface).collidepoint(event.pos):
                _, capture = button_state(self.game, self.selected, self.table_selected)
                if capture is not None:
                    self.play(hand[self.selected], capture)

            # click a table card to toggle its highlight
            elif table_index is not None and table_index < len(self.game.table):
                self.table_selected ^= {table_index}

            # click a hand card to select it, click it again to deselect
            elif index is not None and index < len(hand):
                self.selected = None if index == self.selected else index

        elif event.type == pygame.KEYDOWN:
            # keys 1-3 select a hand card too; only the button plays it
            index = event.key - pygame.K_1
            if 0 <= index < len(self.hand()):
                self.selected = index

    def draw(self, surface):
        label, capture = button_state(self.game, self.selected, self.table_selected)
        render.draw(
            surface,
            self.app.resources,
            self.game,
            self.selected,
            self.table_selected,
            (label, capture is not None),
        )
