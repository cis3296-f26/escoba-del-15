import pygame

from escoba.core.player import Player
from escoba.core.game import Game
from escoba.core.result import GameResult
from escoba.core.rules import end_turn, find_captures, play_card, start_round
from escoba.core.cpu import choose_cpu_move
from escoba.graphics import render
from escoba.graphics.roundover import draw_round_over
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
    return game

def round_finished(state):
    return ( isinstance(state, Game) and not any(s.hand for s in state.player_states.values()))

def main():
    screen = render.create_window(
        SCREEN_WIDTH, SCREEN_HEIGHT, "Escoba del 15"
    )
    resources = Resources()

    clock = pygame.time.Clock()

    players = (Player(0, "You"), Player(1, "CPU", is_cpu=True))
    state = None
    cpu_ready_at = None
    round_over = False
    running = True

    while running:
        # 1. handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif round_over:
                    if event.key == pygame.K_RETURN:
                        round_over = False
                        cpu_ready_at = None
                        start_round(state)

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
                        round_over = round_finished(state)
                elif isinstance(state, GameResult):
                    if event.key == pygame.K_SPACE:
                        state = new_game(state.players)

                    elif event.key == pygame.K_n:
                        state = None

        # 2. let the cpu play after a short pause
        if not round_over and isinstance(state, Game) and state.players[state.turn].is_cpu:
            now = pygame.time.get_ticks()
            if cpu_ready_at is None:
                cpu_ready_at = now + CPU_DELAY_MS
            elif now >= cpu_ready_at:
                cpu_ready_at = None
                state = take_turn(state, *choose_cpu_move(state))
                round_over = round_finished(state)

        if round_over:
            draw_round_over(screen, state)
        else:
            render.draw(screen, resources, state)

        # swap buffers
        pygame.display.flip()

        # 3. Wait so the loop runs at a steady frame rate
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
