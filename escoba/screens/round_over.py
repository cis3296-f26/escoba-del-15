import pygame

from escoba.core.rules import start_round
from escoba.graphics.roundover import draw_round_over
from escoba.screens.screen import Screen


class RoundOverScreen(Screen):
    def __init__(self, app, game_screen):
        self.app = app
        self.game_screen = game_screen

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            start_round(self.game_screen.game)
            self.game_screen.schedule_cpu()
            self.app.change_screen(self.game_screen)

    def draw(self, surface):
        draw_round_over(surface, self.game_screen.game)
