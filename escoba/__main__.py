import random
import pygame

from escoba.core.cards import Card, Suit, new_deck
from escoba.core.gamestate import GameState
from escoba.graphics.cards import CardRenderer
from escoba.graphics.render import RenderEngine

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
    card_renderer = CardRenderer()

    clock = pygame.time.Clock()

    running = True

    players = ["You", "CPU"]
    state = GameState(players, new_deck(), [])

    while running:
        # 1. handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            
            # TODO: remove this temp testing key
            elif event.type == pygame.KEYDOWN and not state.is_game_over() and event.key == pygame.K_n:
                state.add_round_scores({player: random.randint(0, 6) for player in players})
            elif event.type == pygame.KEYDOWN and state.is_game_over() and event.key == pygame.K_r:
                state = GameState(players, new_deck(), [])

        # 2.
        # begin frame
        screen.fill(SCREEN_COLOR_BACKGROUND)

        # 3. render the current game state
        if state.is_game_over():
            render_engine.draw_end_board(screen, state)
        else:
            card_renderer.draw(
                screen, 
                Card(Suit.OROS, 7), 
                (50, 50)
            )

            card_renderer.draw(
                screen, 
                Card(Suit.OROS, 7), 
                (150, 50),
                face_up=False
            )
        
            card_renderer.draw(
                screen, 
                None, 
                (250, 50)
            )

        # swap buffers
        pygame.display.flip()

        # 3. Wait so the loop runs at a steady frame rate
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
