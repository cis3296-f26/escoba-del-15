import pygame

from escoba.core.player import Player
from escoba.core.game import Game
from escoba.core.result import GameResult
from escoba.core.rules import end_turn, is_legal_capture, play_card, start_round
from escoba.core.cpu import choose_cpu_move
from escoba.graphics import render
from escoba.graphics.board import button_rect, hand_card_at, table_card_at
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

def button_state(game, selected, table_selected):
    # (label, capture or None when disabled) for the discard/capture button
    if game.players[game.turn].is_cpu or selected is None:
        return "Discard", None

    card = game.player_states[game.current_player_id].hand[selected]
    capture = tuple(game.table[i] for i in sorted(table_selected))

    if not capture:
        return "Discard", ()
    if is_legal_capture(card, capture, game.table):
        return "Capture", capture
    return "Capture", None

def main():
    screen = render.create_window(
        SCREEN_WIDTH, SCREEN_HEIGHT, "Escoba del 15"
    )
    resources = Resources()

    clock = pygame.time.Clock()

    players = (Player(0, "You"), Player(1, "CPU", is_cpu=True))
    state = None
    cpu_ready_at = None
    selected = None  # index of the selected card in your hand
    table_selected = set()  # indices of highlighted table cards

    running = True

    while running:
        # 1. handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # select cards by clicking; only the button makes a move
                if isinstance(state, Game) and not state.players[state.turn].is_cpu:
                    hand = state.player_states[state.current_player_id].hand
                    index = hand_card_at(screen, event.pos)
                    table_index = table_card_at(screen, event.pos, len(state.table))

                    label, capture = button_state(state, selected, table_selected)

                    # the button plays the selected card as a discard or capture
                    if button_rect(screen).collidepoint(event.pos):
                        if capture is not None:
                            card = hand[selected]
                            selected = None
                            table_selected = set()
                            state = take_turn(state, card, capture)

                    # click a table card to toggle its highlight
                    elif table_index is not None and table_index < len(state.table):
                        table_selected ^= {table_index}

                    # click a hand card to select it, click it again to deselect
                    elif index is not None and index < len(hand):
                        selected = None if index == selected else index

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif state is None:
                    if event.key == pygame.K_SPACE:
                        state = new_game(players)

                elif isinstance(state, Game):
                    # keys 1-3 select a hand card too; only the button plays it
                    player = state.players[state.turn]
                    hand = state.player_states[player.id].hand
                    index = event.key - pygame.K_1

                    if player.is_cpu:
                        pass

                    elif 0 <= index < len(hand):
                        selected = index

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
                table_selected = set()
                state = take_turn(state, *choose_cpu_move(state))

        button = None
        if isinstance(state, Game):
            label, capture = button_state(state, selected, table_selected)
            button = (label, capture is not None)

        render.draw(screen, resources, state, selected, table_selected, button)

        # swap buffers
        pygame.display.flip()

        # 3. Wait so the loop runs at a steady frame rate
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
