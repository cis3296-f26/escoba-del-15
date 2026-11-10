import pygame

from escoba.core.player import Player
from escoba.core.game import Game
from escoba.core.result import GameResult
from escoba.core.rules import end_turn, is_legal_capture, play_card, start_round
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

def update_selection(pos, clickable, card, capture):
    # clicking a hand card picks it (click again to unpick)
    for hand_card, rect in clickable["hand"]:
        if rect.collidepoint(pos):
            return (None if hand_card == card else hand_card), []

    # clicking table cards toggles them in the capture
    for table_card, rect in clickable["table"]:
        if rect.collidepoint(pos):
            if table_card in capture:
                return card, [c for c in capture if c != table_card]
            return card, capture + [table_card]

    return card, capture

def main():
    screen = render.create_window(
        SCREEN_WIDTH, SCREEN_HEIGHT, "Escoba del 15"
    )
    resources = Resources()

    clock = pygame.time.Clock()

    players = (Player(0, "You"), Player(1, "CPU", is_cpu=True))
    state = None
    cpu_ready_at = None

    # what the player has clicked so far, and where the cards were last drawn
    selected_card = None
    selected_table = []
    clickable = None

    running = True

    while running:
        # 1. handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif (
                event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                and isinstance(state, Game) and clickable
                and not state.players[state.turn].is_cpu
            ):
                selected_card, selected_table = update_selection(
                    event.pos, clickable, selected_card, selected_table
                )

                # plays as soon as the picked cards add up to 15
                if (
                    selected_card is not None and selected_table
                    and is_legal_capture(selected_card, selected_table, state.table)
                ):
                    state = take_turn(state, selected_card, selected_table)
                    selected_card, selected_table = None, []

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif state is None:
                    if event.key == pygame.K_SPACE:
                        state = new_game(players)

                elif isinstance(state, Game):
                    # space puts the picked card down without capturing
                    if (
                        event.key == pygame.K_SPACE and selected_card is not None
                        and not state.players[state.turn].is_cpu
                    ):
                        state = take_turn(state, selected_card, ())
                        selected_card, selected_table = None, []

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

        selected = [selected_card, *selected_table] if selected_card else selected_table
        clickable = render.draw(screen, resources, state, selected)

        # swap buffers
        pygame.display.flip()

        # 3. Wait so the loop runs at a steady frame rate
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
