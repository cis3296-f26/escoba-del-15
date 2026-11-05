import random
import pygame

from escoba.core.player import Player
from escoba.core.gamestate import GameState 
from escoba.graphics.render import RenderEngine, CARD_WIDTH, CARD_HEIGHT
from escoba.core.deck import Deck

from escoba.graphics.render import RenderEngine
from escoba.graphics.board import BoardRenderer

# the game draws to a small fixed-size canvas (pixel-art resolution)
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640

SCREEN_COLOR_BACKGROUND = (61, 153, 112) #Olive

FPS = 60


def create_game():
    # Create players
    players = [
        Player("You"),
        Player("CPU", is_cpu=True)
    ]

    # Create and shuffle deck
    deck = Deck()
    deck.shuffle()

    # Deal four cards to the table
    table = [deck.draw() for _ in range(4)]

    # Create GameState
    state = GameState(players, deck, table)

    # Deal three cards to each player
    state.deal_cards()

    return state


def main():
    pygame.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)
    pygame.display.set_caption("Escoba del 15")

    clock = pygame.time.Clock()

    render_engine = RenderEngine()
    renderer = BoardRenderer()

    # Initialize GameState
    state = create_game()

    running = True

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

        if state.is_game_over():
            render_engine.draw_end_board(screen, state)
        else:
            renderer.draw(
                screen,
                state.table,
                [player.hand for player in state.players],
                len(state.deck)
            )

        # swap buffers
        pygame.display.flip()

        # 3. Wait so the loop runs at a steady frame rate
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
