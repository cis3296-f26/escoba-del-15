from escoba.core.rules import is_legal_capture
from escoba.graphics.board import hand_rects, move_button, table_rects


class MoveSelection:
    def __init__(self):
        self.card = None
        self.capture = []

    def can_play(self, table):
        return self.card is not None and is_legal_capture(self.card, self.capture, table)

    def click(self, bounds, position, game):
        if move_button(bounds).collidepoint(position):
            return (self.card, tuple(self.capture)) if self.can_play(game.table) else None

        hand = game.player_states[game.current_player_id].hand
        rects = hand_rects(bounds, game.turn, len(game.players), len(hand))
        for card, rect in zip(hand, rects):
            if rect.collidepoint(position):
                self.card = None if self.card == card else card
                return None

        # a long table overlaps its cards, so check the topmost (last drawn) first
        rects = table_rects(bounds, len(game.table), len(game.deck))
        for card, rect in reversed(list(zip(game.table, rects))):
            if rect.collidepoint(position):
                if card in self.capture:
                    self.capture.remove(card)
                else:
                    self.capture.append(card)
                return None

        return None
