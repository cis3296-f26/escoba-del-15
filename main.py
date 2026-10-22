"""Escoba del 15: entry point. Opens the game window and runs the main loop."""
import pygame

# the game draws to a small fixed-size canvas (pixel-art resolution)
CANVAS_WIDTH = 320
CANVAS_HEIGHT = 180
FPS = 30
BACKGROUND = (0, 0, 0)

def main():
    pygame.init()
    screen - pygame.display.set_mode((CANVAS_WIDTH, CANVAS_HEIGHT))
    pygame.display.set_caption("Escoba del 15")
    clock = pygame.time.Clock()

    running = True
    while running:
        # 1. handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # 2. draw the frame
        screen.fill(BACKGROUND)
        pygame.display.flip()

        # 3. Wait so the loop runs at a steady frame rate
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
