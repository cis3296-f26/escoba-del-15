# one class per screen; main() runs whichever scene is current
#
# handle_event and update return the scene to switch to, or None to stay

import pygame

from escoba.core.cpu import choose_cpu_move
from escoba.core.game import Game
from escoba.core.rules import end_turn, play_card, start_round
from escoba.graphics.board import draw_board, move_button
from escoba.graphics.capture import MoveAnimation
from escoba.graphics.colors import BLACK, GRAY, WHITE
from escoba.graphics.render import draw_popup
from escoba.input import MoveSelection


CPU_DELAY_MS = 800


class Scene:
    def __init__(self, bounds, resources):
        self.bounds = bounds
        self.resources = resources

    def update(self, now):
        return None


class MenuScene(Scene):
    def __init__(self, bounds, resources, players):
        super().__init__(bounds, resources)
        self.players = players

    def handle_event(self, event, now):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            return PlayScene(self.bounds, self.resources, self.players)
        return None

    def draw(self, screen, now):
        draw_popup(screen, self.resources, "Escoba", ["Press Space to start", "Press Esc to quit"])


class PlayScene(Scene):
    def __init__(self, bounds, resources, players):
        super().__init__(bounds, resources)
        self.game = Game(players)
        start_round(self.game)
        self.selection = MoveSelection()
        self.animation = None
        self.cpu_ready_at = None

    def handle_event(self, event, now):
        game = self.game
        if self.animation is not None or game.players[game.turn].is_cpu:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            move = self.selection.click(self.bounds, event.pos, game)
            if move is not None:
                self.animation = MoveAnimation(self.bounds, game, move, now)
                self.selection = MoveSelection()

    def update(self, now):
        if self.animation is not None:
            if now < self.animation.ends_at:
                return None
            result = self.finish_move(*self.animation.move)
            self.animation = None
            if result is not None:
                return GameOverScene(self.bounds, self.resources, result)

        game = self.game
        if game.players[game.turn].is_cpu:
            if self.cpu_ready_at is None:
                self.cpu_ready_at = now + CPU_DELAY_MS
            elif now >= self.cpu_ready_at:
                self.animation = MoveAnimation(self.bounds, game, choose_cpu_move(game), now)
                self.cpu_ready_at = None

        return None

    def finish_move(self, card, capture):
        game = self.game
        play_card(game, card, capture)
        result = end_turn(game)
        # everyone is out of cards and the deck is empty, but nobody has won: deal a new round
        if result is None and not any(state.hand for state in game.player_states.values()):
            start_round(game)
        return result

    def draw(self, screen, now):
        game, selection, animation = self.game, self.selection, self.animation

        draw_board(
            screen,
            self.resources,
            game,
            selected={selection.card, *selection.capture},
            hidden=animation.origins if animation else (),
        )

        # the button reads Capture or Discard and is grayed out until the selection is legal
        if not game.players[game.turn].is_cpu:
            button = move_button(self.bounds)
            enabled = selection.can_play(game.table)
            pygame.draw.rect(screen, BLACK if enabled else GRAY, button, border_radius=8)
            capture = animation.move[1] if animation else selection.capture
            text = self.resources.text_font.render(
                "Capture" if capture else "Discard", True, WHITE if enabled else BLACK
            )
            screen.blit(text, text.get_rect(center=button.center))

        if animation:
            animation.draw(screen, self.resources, now)


class GameOverScene(Scene):
    def __init__(self, bounds, resources, result):
        super().__init__(bounds, resources)
        self.result = result

    def handle_event(self, event, now):
        if event.type != pygame.KEYDOWN:
            return None
        if event.key == pygame.K_SPACE:
            return PlayScene(self.bounds, self.resources, self.result.players)
        if event.key == pygame.K_n:
            return MenuScene(self.bounds, self.resources, self.result.players)
        return None

    def draw(self, screen, now):
        result = self.result
        winner = next(p for p in result.players if p.id == result.winner_id)
        scores = dict(result.scores)
        lines = [f"Winner: {winner.name}"]
        lines.extend(f"{p.name}: {scores[p.id]}" for p in result.players)
        lines.extend(["Press Space to play again", "Press N to return to menu"])
        draw_popup(screen, self.resources, "Game Over", lines)
