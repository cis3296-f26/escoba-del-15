import pygame

from escoba.core.player import Player
from escoba.graphics import render
from escoba.graphics.resources import Resources
from escoba.screens import MenuScreen, Screen

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
FPS = 30


class App:
    # owns the window and the active screen; screens call change_screen to move on
    def __init__(self):
        self.surface = render.create_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Escoba del 15")
        self.resources = Resources()
        players = (Player(0, "You"), Player(1, "CPU", is_cpu=True))
        self.screen: Screen = MenuScreen(self, players)

    def change_screen(self, screen: Screen):
        self.screen = screen

    def run(self):
        clock = pygame.time.Clock()
        while True:
            # quit and Esc work on every screen
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    pygame.quit()
                    return
                self.screen.handle_event(event)

            self.screen.draw(self.surface)
            pygame.display.flip()
            clock.tick(FPS)


if __name__ == "__main__":
    App().run()
