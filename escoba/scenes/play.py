import pygame

from escoba.actions import Action, Input
from escoba.core.cpu import choose_cpu_move
from escoba.core.result import GameResult, RoundResult
from escoba.core.rules import end_turn, is_legal_capture, new_game, play_card
from escoba.graphics.board import board_items
from escoba.graphics.card_sprite import CardSprite
from escoba.scenes.scene import Scene
from escoba.ui.button import Button
from escoba.ui.layer import Layer

# board focus is 2d (zone row + index), scene.py's _MOVE is 1d for modal buttons
_MOVE = {
    Action.MOVE_LEFT: (-1, 0),
    Action.MOVE_RIGHT: (1, 0),
    Action.MOVE_UP: (0, -1),
    Action.MOVE_DOWN: (0, 1)
}

class ZoneFocus:
    # keyboard cursor across table / buttons / hand
    def __init__(self, zone="hand", index=0):
        self.zone = zone
        self.index = index

    @property
    def cursor(self):
        return (self.zone, self.index)

    @cursor.setter
    def cursor(self, value):
        self.zone, self.index = value

    def clamp(self, zones, lengths):
        if self.zone not in zones:
            self.zone = zones[-1]

        count = lengths[self.zone]
        self.index = 0 if count == 0 else max(0, min(self.index, count - 1))

    def move(self, dx, dy, zones, lengths):
        self.clamp(zones, lengths)

        if dy:
            zone_index = max(0, min(len(zones) - 1, zones.index(self.zone) + dy))
            self.zone = zones[zone_index]

        count = lengths[self.zone]
        self.index = 0 if count == 0 else max(0, min(self.index + dx, count - 1))

    def set(self, zone, index):
        self.zone = zone
        self.index = index

class PlayScene(Scene):
    def __init__(self, ctx, game=None):
        super().__init__(ctx)
        self.game = game if game is not None else new_game(ctx.players)
        self.hand_i = None
        self.table_sel = set()
        self.zone_focus = ZoneFocus("hand", 0)
        self.board = Layer()
        self.add(self.board)
        self.sync()

    def is_cpu_turn(self):
        return self.game.players[self.game.turn].is_cpu

    def settle(self):
        # player input snaps mid-lerp so hits and the next sync start from goals
        if not self.board.idle:
            self.board.snap_all()

    def hand(self):
        return self.game.player_states[self.game.current_player_id].hand

    def zones(self):
        rows = []
        if self.game.table:
            rows.append("table")
        rows.append("buttons")
        if self.hand():
            rows.append("hand")
        return rows

    def zone_lengths(self):
        return {"hand": len(self.hand()), "table": len(self.game.table), "buttons": 2}

    def clear_selection(self):
        self.hand_i = None
        self.table_sel = set()
        self.zone_focus.set("hand", 0)

    def legal_capture(self):
        if self.hand_i is None or not self.table_sel:
            return None

        card = self.hand()[self.hand_i]
        taken = tuple(self.game.table[i] for i in sorted(self.table_sel))
        return taken if is_legal_capture(card, taken, self.game.table) else None

    def sync(self):
        # card tags keep one view while sprites lerp hand↔table↔pile
        hand_selected = () if self.hand_i is None else (self.hand_i,)
        states = self.game.player_states
        ctx = self.ctx
        self.board.sync(board_items(
            ctx.surface,
            self.game.table,
            [states[player.id].hand for player in self.game.players],
            [states[player.id].captured for player in self.game.players],
            len(self.game.deck),
            hand_selected=hand_selected,
            table_selected=self.table_sel,
            player_names=tuple(player.name for player in self.game.players),
            discard_label=ctx.text("button_discard"),
            capture_label=ctx.text("button_capture"),
            discard_on=self.hand_i is not None,
            capture_on=self.legal_capture() is not None,
            show_buttons=not self.is_cpu_turn()))

    def play(self, card, capture):
        self.clear_selection()
        play_card(self.game, card, capture)
        result = end_turn(self.game)
        self.sync()

        if isinstance(result, RoundResult):
            from escoba.scenes.overlays import RoundOverScene
            return RoundOverScene(self, result)
        if isinstance(result, GameResult):
            from escoba.scenes.overlays import GameOverScene
            return GameOverScene(self, result)
        return None

    def try_discard(self):
        if self.hand_i is None:
            return None
        return self.play(self.hand()[self.hand_i], ())

    def try_capture(self):
        taken = self.legal_capture()
        if taken is None:
            return None
        return self.play(self.hand()[self.hand_i], taken)

    def toggle(self, zone=None, index=None):
        zone, index = self.zone_focus.cursor if zone is None else (zone, index)

        if zone == "hand":
            if 0 <= index < len(self.hand()):
                self.hand_i = None if self.hand_i == index else index
        elif zone == "table" and 0 <= index < len(self.game.table):
            self.table_sel ^= {index}

    def activate_button(self, index):
        if index == 0:
            return self.try_discard()
        if index == 1:
            return self.try_capture()
        return None

    def inputs_from_event(self, event):
        if self.is_cpu_turn():
            return []
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return []

        self.settle()
        hit = self.hit_element(event.pos)
        if hit is None:
            return []

        if isinstance(hit, Button):
            bound = hit.input_at(event.pos)
            return [bound] if bound is not None else []

        if isinstance(hit, CardSprite) and hit.zone in ("hand", "table"):
            self.zone_focus.set(hit.zone, hit.index)
            return [Input(Action.SELECT)]

        return []

    def handle_input(self, bound: Input):
        if self.is_cpu_turn():
            return None

        self.settle()

        if bound.action in _MOVE:
            self.zone_focus.move(*_MOVE[bound.action], self.zones(), self.zone_lengths())
            return None

        if bound.action == Action.SELECT:
            self.zone_focus.clamp(self.zones(), self.zone_lengths())
            zone, index = self.zone_focus.cursor
            if zone == "buttons":
                return self.activate_button(index)
            self.toggle()
            self.sync()
            return None

        if bound.action == Action.DISCARD:
            return self.try_discard()
        if bound.action == Action.CAPTURE:
            return self.try_capture()
        return None

    def on_update(self, dt):
        # CPU waits for travel so its plays stay readable
        if self.is_cpu_turn() and self.board.idle:
            return self.play(*choose_cpu_move(self.game))
        return None

    def draw(self, surface, dt):
        if not self.is_cpu_turn():
            self.zone_focus.clamp(self.zones(), self.zone_lengths())
            self.board.focus_tag = self.zone_focus.cursor
        else:
            self.board.focus_tag = None

        super().draw(surface, dt)
