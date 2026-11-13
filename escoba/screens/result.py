import pygame

from escoba.graphics import render
from escoba.screens.game import GameScreen
from escoba.screens.menu import MenuScreen
from escoba.screens.screen import Screen


class ResultScreen(Screen):
    def __init__(self, app, result):
        self.app = app
        self.result = result

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_SPACE:
            self.app.change_screen(GameScreen(self.app, self.result.players))

        elif event.key == pygame.K_n:
            self.app.change_screen(MenuScreen(self.app, self.result.players))

    def draw(self, surface):
        render.draw(surface, self.app.resources, self.result)
