import pygame

from escoba.core.player import Player
from escoba.graphics import render
from escoba.graphics.colors import OLIVE
from escoba.graphics.resources import Resources
from escoba.scenes import MenuScene

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640

FPS = 30

def main():
    screen = render.create_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Escoba del 15")
    clock = pygame.time.Clock()

    players = (Player(0, "You"), Player(1, "CPU", is_cpu=True))
    scene = MenuScene(screen.get_rect(), Resources(), players)

    running = True
    while running:
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
                break
            scene = scene.handle_event(event, now) or scene

        if not running:
            break

        scene = scene.update(now) or scene
        screen.fill(OLIVE)
        scene.draw(screen, now)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
