import random
import pygame

from escoba.core.player import Player
from escoba.core.game import Game, GameState
from escoba.graphics.render import RenderEngine, CARD_WIDTH, CARD_HEIGHT
from escoba.core.deck import Deck

from escoba.graphics.render import RenderEngine

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
    game = Game(players, deck, table)

    # Deal three cards to each player
    game.deal_cards()

    return game


def main():
    pygame.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)
    pygame.display.set_caption("Escoba del 15")

    clock = pygame.time.Clock()

    render_engine = RenderEngine()

    # Initialize GameState
    game = create_game()

    running = True

    while running:
        # 1. handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif game.state == GameState.START:
                    if event.key == pygame.K_RETURN:
                        game.state = GameState.PLAY

                elif game.state == GameState.PLAY:
                    # TODO: remove this temp testing key
                    if event.key == pygame.K_n:
                        game.add_round_scores({
                            player: random.randint(0, 6)
                            for player in game.players
                        })

                elif game.state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        game = create_game()
                        game.state = GameState.PLAY

        # 2. update game state
        if game.state == GameState.PLAY and game.is_game_over():
            game.state = GameState.GAME_OVER

        render_engine.draw(screen, game)

        # swap buffers
        pygame.display.flip()

        # 3. Wait so the loop runs at a steady frame rate
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
