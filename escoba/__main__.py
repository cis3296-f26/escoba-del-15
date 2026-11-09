import pygame

from escoba.core.player import Player
from escoba.core.game import Game
from escoba.core.result import GameResult
from escoba.core.rules import end_turn, find_captures, play_card, start_round
from escoba.core.cpu import choose_cpu_move
from escoba.graphics import render
from escoba.graphics.resources import Resources

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640

FPS = 30

# how long the cpu "thinks" before playing
CPU_DELAY_MS = 800

def new_game(players):
    game = Game(players)
    start_round(game)
    return game

def take_turn(game, card, capture):
    # play a card, then deal / end the round / end the game as needed
    play_card(game, card, capture)
    result = end_turn(game)
    if result is not None:
        return result

    # hands empty here means the round just ended without a winner
    # todo: round summary screen goes here before the next round
    if not any(state.hand for state in game.player_states.values()):
        start_round(game)

    return game

def main():
    screen = render.create_window(
        SCREEN_WIDTH, SCREEN_HEIGHT, "Escoba del 15"
    )
    resources = Resources()

    clock = pygame.time.Clock()

    players = (Player(0, "You"), Player(1, "CPU", is_cpu=True))
    state = None
    cpu_ready_at = None

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
                        state = new_game(players)

                elif isinstance(state, Game):
                    # todo: temp keys 1-3, replaced by card click input
                    player = state.players[state.turn]
                    hand = state.player_states[player.id].hand
                    index = event.key - pygame.K_1

                    if not player.is_cpu and 0 <= index < len(hand):
                        card = hand[index]
                        captures = find_captures(card, state.table)
                        state = take_turn(state, card, captures[0] if captures else ())

                elif isinstance(state, GameResult):
                    if event.key == pygame.K_SPACE:
                        state = new_game(state.players)

                    elif event.key == pygame.K_n:
                        state = None

        # 2. let the cpu play after a short pause
        if isinstance(state, Game) and state.players[state.turn].is_cpu:
            now = pygame.time.get_ticks()
            if cpu_ready_at is None:
                cpu_ready_at = now + CPU_DELAY_MS
            elif now >= cpu_ready_at:
                cpu_ready_at = None
                state = take_turn(state, *choose_cpu_move(state))

        render.draw(screen, resources, state)

        # swap buffers
        pygame.display.flip()

        # 3. Wait so the loop runs at a steady frame rate
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
