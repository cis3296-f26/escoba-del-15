import pygame

from escoba.core.player import Player
from escoba.core.game import Game
from escoba.core.result import GameResult
from escoba.graphics import render
from escoba.graphics.resources import Resources

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640

FPS = 30

def main():
    screen = render.create_window(
        SCREEN_WIDTH, SCREEN_HEIGHT, "Escoba del 15"
    )
    resources = Resources()

    clock = pygame.time.Clock()

    players = (Player(0, "You"), Player(1, "CPU", is_cpu=True))
    state = None

    running = True

    while running:
        # 1. handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif state is None:
                    if event.key == pygame.K_SPACE:
                        state = Game(players)

                elif isinstance(state, Game):
                    # temp for testing game-over screen
                    if event.key == pygame.K_n:
                        state = GameResult(
                            players=state.players,
                            winner_id=state.players[0].id,
                            scores=tuple(
                                (p.id, state.player_states[p.id].score)
                                for p in state.players
                            )
                        )

                    # todo: card input will go here

                elif isinstance(state, GameResult):
                    if event.key == pygame.K_SPACE:
                        state = Game(state.players)

                    elif event.key == pygame.K_n:
                        state = None

        render.draw(screen, resources, state)

        # swap buffers
        pygame.display.flip()

        # 3. Wait so the loop runs at a steady frame rate
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()