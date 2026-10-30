import pygame

from escoba.graphics.cards import CardRenderer, CARD_WIDTH, CARD_HEIGHT

TABLE_COLOR = (61, 153, 112) #Olive

CARD_SPACING = 8
TABLE_PADDING = 20

class BoardRenderer:
    def __init__(self):
        self.card_renderer = CardRenderer()

    def _draw_hand(self, screen, cards, x, y, face_up, vertical=False):
        if not cards: return

        card_size = CARD_HEIGHT if vertical else CARD_WIDTH
        spacing = card_size + CARD_SPACING
        total_size = len(cards) * card_size + (len(cards) - 1) * CARD_SPACING

        center = y if vertical else x
        start = center - total_size // 2

        for i, card in enumerate(cards):
            offset = start + i * spacing
            position = (x, offset) if vertical else (offset, y)

            self.card_renderer.draw(screen, card, position, face_up)

    def draw(self, screen, table_cards, player_hands, deck_count):
        screen.fill(TABLE_COLOR)

        width, height = screen.get_size()
        center_x, center_y = width // 2, height // 2

        # Cards on the table
        self._draw_hand(
            screen,
            table_cards,
            center_x,
            center_y - CARD_HEIGHT // 2,
            face_up=True
        )

        # Remaining deck
        if deck_count > 0:
            self.card_renderer.draw(
                screen,
                None,
                (center_x + 160, center_y - CARD_HEIGHT // 2),
                face_up=False
            )

        # Player positions: bottom, top, left, right
        positions = [
            (center_x, height - CARD_HEIGHT - TABLE_PADDING),
            (center_x, TABLE_PADDING),
            (TABLE_PADDING, center_y),
            (width - CARD_WIDTH - TABLE_PADDING, center_y)
        ]

        for i, hand in enumerate(player_hands):
            x, y = positions[i]

            self._draw_hand(
                screen,
                hand,
                x,
                y,
                face_up=False,
                vertical=i >= 2
            )