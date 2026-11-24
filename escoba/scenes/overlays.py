import pygame

from escoba.actions import Action, Input
from escoba.core.result import GameResult, RoundResult
from escoba.core.rules import start_round
from escoba.core.rules import new_game
from escoba.scenes.play import PlayScene
from escoba.scenes.scene import Scene

_ROUND_CATS = (
    ("most_cards", "round_cat_most_cards"),
    ("most_oros", "round_cat_most_oros"),
    ("most_sevens", "round_cat_most_sevens"),
    ("velo", "round_cat_velo"),
    ("escobas", "round_cat_escobas")
)

def _draw_over_play(scene, surface, dt):
    # board stays under the modal
    scene.play.draw(surface, dt)

    veil = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    veil.fill((0, 0, 0, 120))
    surface.blit(veil, (0, 0))

    scene.draw_elements(surface, clear=False)

def round_lines(ctx, game, result: RoundResult):
    names = [player.name for player in game.players]

    def fmt(label, values):
        parts = ", ".join(f"{name}: {value}" for name, value in zip(names, values))
        return f"{label}: {parts}"

    lines = [
        fmt(ctx.text(string_id), [getattr(entry, attr) for entry in result.breakdown])
        for attr, string_id in _ROUND_CATS
    ]
    lines.append(fmt(ctx.text("round_cat_round_points"), [entry.round_total for entry in result.breakdown]))
    lines.append(fmt(ctx.text("round_cat_total"), result.totals))
    return lines

class MenuScene(Scene):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.add_overlay(
            ctx.text("menu_title"),
            [ctx.text("menu_quit", key=ctx.binds.label(Action.QUIT))],
            [(ctx.text("menu_start"), Action.SELECT)])

    def on_input(self, bound: Input):
        if bound.action == Action.SELECT:
            return PlayScene(self.ctx)
        return None

class RoundOverScene(Scene):
    def __init__(self, play, result: RoundResult):
        super().__init__(play.ctx)
        self.play = play
        ctx = play.ctx
        self.add_overlay(
            ctx.text("round_over_title"),
            round_lines(ctx, play.game, result),
            [(ctx.text("round_continue"), Action.SELECT)])

    def on_input(self, bound: Input):
        if bound.action == Action.SELECT:
            start_round(self.play.game)
            self.play.clear_selection()
            self.play.sync()
            return self.play
        return None

    def draw(self, surface, dt):
        _draw_over_play(self, surface, dt)

class GameOverScene(Scene):
    def __init__(self, play, result: GameResult):
        super().__init__(play.ctx)
        self.play = play
        ctx = play.ctx
        winner = next(player for player in result.players if player.id == result.winner_id)
        scores = dict(result.scores)
        lines = [ctx.text("winner_line", name=winner.name)]
        lines.extend(
            ctx.text("score_line", name=player.name, score=scores[player.id])
            for player in result.players)
        lines.append(ctx.text("rematch_prompt"))

        self.add_overlay(
            ctx.text("game_over_title"),
            lines,
            [(ctx.text("rematch_yes"), Action.SELECT), (ctx.text("rematch_no"), Action.CANCEL)])

    def on_input(self, bound: Input):
        if bound.action == Action.SELECT:
            self.play.game = new_game(self.play.ctx.players)
            self.play.clear_selection()
            self.play.sync()
            return self.play

        if bound.action == Action.CANCEL:
            return MenuScene(self.play.ctx)

        return None

    def draw(self, surface, dt):
        _draw_over_play(self, surface, dt)
