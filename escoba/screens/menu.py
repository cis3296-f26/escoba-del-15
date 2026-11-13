import pygame

from escoba.graphics import render
from escoba.screens.game import GameScreen
from escoba.screens.screen import Screen


class MenuScreen(Screen):
    def __init__(self, app, players):
        self.app = app
        self.players = players

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.app.change_screen(GameScreen(self.app, self.players))

    def draw(self, surface):
        render.draw(surface, self.app.resources, None)
