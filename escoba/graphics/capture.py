import pygame

from escoba.graphics.board import capture_stack_position, card_row, hand_rects, table_rects
from escoba.graphics.cards import CARD_HEIGHT, CARD_WIDTH, draw_card

MOVE_DURATION_MS = 360
CAPTURE_PAUSE_MS = 2000
FLIP_DURATION_MS = 160


class MoveAnimation:
    def __init__(self, bounds, game, move, started_at):
        self.move = move
        self.started_at = started_at
        card, capture = move
        player_count = len(game.players)
        state = game.player_states[game.current_player_id]
        hand = hand_rects(bounds, game.turn, player_count, len(state.hand))
        hand_origin = hand[state.hand.index(card)].topleft
        table_rows = table_rects(bounds, len(game.table), len(game.deck))
        table = {table_card: rect.topleft for table_card, rect in zip(game.table, table_rows)}

        if capture:
            # gather the cards mid-screen, then sweep them onto the capture stack
            self.origins = {card: hand_origin, **{taken: table[taken] for taken in capture}}
            middle = card_row(bounds.centerx, bounds.centery - CARD_HEIGHT // 2, len(self.origins))
            self.staging = {moved: rect.topleft for moved, rect in zip(self.origins, middle)}
            stack = capture_stack_position(bounds, game.turn, player_count, state.capture_count)
            self.destinations = dict.fromkeys(self.origins, stack)
            self.ends_at = started_at + 2 * MOVE_DURATION_MS + CAPTURE_PAUSE_MS + FLIP_DURATION_MS
        else:
            # the discard joins the table, which may re-center
            self.origins = {**table, card: hand_origin}
            new_table = table_rects(bounds, len(self.origins), len(game.deck))
            self.destinations = {moved: rect.topleft for moved, rect in zip(self.origins, new_table)}
            self.ends_at = started_at + MOVE_DURATION_MS

    def draw(self, screen, resources, now):
        elapsed = now - self.started_at
        origins, destinations = self.origins, self.destinations
        if self.move[1]:
            sweep = elapsed - MOVE_DURATION_MS - CAPTURE_PAUSE_MS
            if sweep < 0:
                destinations = self.staging
                screen.fill((110, 110, 110), special_flags=pygame.BLEND_RGB_MULT)
            elif sweep < MOVE_DURATION_MS:
                origins, elapsed = self.staging, sweep
            else:
                # flip the top card face down by squeezing it to zero width and back
                card = self.move[1][-1]
                progress = min(1, (sweep - MOVE_DURATION_MS) / FLIP_DURATION_MS)
                image = resources.card_faces[card] if progress < 0.5 else resources.card_back
                width = max(1, round(CARD_WIDTH * abs(1 - 2 * progress)))
                x, y = self.destinations[card]
                screen.blit(pygame.transform.scale(image, (width, CARD_HEIGHT)), (x + (CARD_WIDTH - width) // 2, y))
                return

        progress = min(1, elapsed / MOVE_DURATION_MS)
        eased = progress * progress * (3 - 2 * progress)
        for card, origin in origins.items():
            x, y = pygame.Vector2(origin).lerp(destinations[card], eased)
            draw_card(screen, resources, card, (round(x), round(y)))
