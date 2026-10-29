"""Escoba del 15: entry point. Opens the game window and runs the main loop."""
import pygame

from escoba.graphics.render import RenderEngine, CARD_WIDTH, CARD_HEIGHT

# the game draws to a small fixed-size canvas (pixel-art resolution)
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 180

SCREEN_COLOR_BACKGROUND = (61, 153, 112) #Olive

FPS = 60

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)
    pygame.display.set_caption("Escoba del 15")

    render_engine = RenderEngine()

    clock = pygame.time.Clock()

    running = True

    # temp cards to test rendering
    cards = [
        ((SCREEN_WIDTH - CARD_WIDTH) / 2, (SCREEN_HEIGHT - CARD_HEIGHT) / 2)
        ]

    while running:
        # 1. handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # 2.
        # begin frame
        screen.fill(SCREEN_COLOR_BACKGROUND)

        render_engine.draw_cards(screen, cards)

        # swap buffers
        pygame.display.flip()

        # 3. Wait so the loop runs at a steady frame rate
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
