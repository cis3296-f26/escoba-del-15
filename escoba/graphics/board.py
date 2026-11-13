import pygame

from escoba.graphics.cards import draw_card, CARD_WIDTH, CARD_HEIGHT
from escoba.graphics.colors import YELLOW, BLACK, WHITE, GRAY, SILVER

CARD_SPACING = 8
EDGE_PADDING = 28
DECK_GAP = 24
HAND_SLOTS = 3
TABLE_SLOTS = 4
SELECT_LIFT = 12
SELECT_BORDER = 3
BUTTON_WIDTH = 110
BUTTON_HEIGHT = 28
BUTTON_GAP = 10

def row_lefts(count, x, max_width=None):
    # left x of each card in a row centered on x; cards overlap to fit max_width
    step = CARD_WIDTH + CARD_SPACING
    total = count * CARD_WIDTH + (count - 1) * CARD_SPACING
    if max_width is not None and total > max_width and count > 1:
        step = (max_width - CARD_WIDTH) / (count - 1)
        total = max_width
    start = x - total / 2
    return [int(start + i * step) for i in range(count)]

def draw_card_row(screen, resources, cards, x, y, face_up, slots, selected=(), max_width=None):
    cards = list(cards)
    if len(cards) < slots:
        cards = cards + [None] * (slots - len(cards))
    if not cards:
        return

    for i, (card, left) in enumerate(zip(cards, row_lefts(len(cards), x, max_width))):
        lift = SELECT_LIFT if i in selected else 0
        pos = (left, int(y) - lift)
        draw_card(screen, resources, card, pos, face_up)
        if i in selected:
            outline = pygame.Rect(pos, (CARD_WIDTH, CARD_HEIGHT)).inflate(SELECT_BORDER * 2, SELECT_BORDER * 2)
            pygame.draw.rect(screen, YELLOW, outline, width=SELECT_BORDER, border_radius=6)

def row_card_at(pos, count, x, y, max_width=None):
    # index of the card slot under pos in a row laid out like draw_card_row, or None
    lefts = row_lefts(count, x, max_width)
    # check right to left so the card drawn on top wins where cards overlap
    for i in reversed(range(count)):
        if pygame.Rect(lefts[i], int(y) - SELECT_LIFT, CARD_WIDTH, CARD_HEIGHT + SELECT_LIFT).collidepoint(pos):
            return i
    return None

def table_layout(screen):
    # deck is pinned to the right edge; the table row stays centered and
    # grows with the number of cards, overlapping once it would reach the deck
    width, height = screen.get_size()
    center_x = width // 2
    deck_x = width - EDGE_PADDING - CARD_WIDTH
    max_width = 2 * min(center_x - EDGE_PADDING, deck_x - DECK_GAP - center_x)
    return center_x, height // 2 - CARD_HEIGHT // 2, max_width, deck_x

def button_rect(screen):
    # small button centered just above your hand (and above a lifted card)
    width, height = screen.get_size()
    rect = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
    rect.centerx = width // 2
    rect.bottom = height - CARD_HEIGHT - EDGE_PADDING - SELECT_LIFT - BUTTON_GAP
    return rect

def draw_button(screen, resources, label, enabled):
    rect = button_rect(screen)
    fill, ink = (WHITE, BLACK) if enabled else (SILVER, GRAY)
    pygame.draw.rect(screen, fill, rect, border_radius=6)
    pygame.draw.rect(screen, ink, rect, width=2, border_radius=6)
    text = resources.button_font.render(label, True, ink)
    screen.blit(text, text.get_rect(center=rect.center))

def hand_card_at(screen, pos):
    width, height = screen.get_size()
    return row_card_at(pos, HAND_SLOTS, width // 2, height - CARD_HEIGHT - EDGE_PADDING)

def table_card_at(screen, pos, table_count):
    x, y, max_width, _ = table_layout(screen)
    return row_card_at(pos, max(table_count, TABLE_SLOTS), x, y, max_width)

def draw_board(screen, resources, table_cards, player_hands, deck_count, selected=(), table_selected=()):
    width, height = screen.get_size()
    center_x = width // 2

    table_x, table_y, table_max_width, deck_x = table_layout(screen)

    draw_card_row(
        screen, resources, table_cards,
        table_x, table_y,
        face_up=True, slots=TABLE_SLOTS, selected=table_selected,
        max_width=table_max_width
    )

    if deck_count > 0:
        screen.blit(resources.card_back, (deck_x, table_y))

    draw_card_row(
        screen, resources, player_hands[0], center_x,
        height - CARD_HEIGHT - EDGE_PADDING,
        face_up=True, slots=HAND_SLOTS, selected=selected
    )

    opponents = player_hands[1:]
    n = len(opponents)
    if n == 0:
        return

    segment = width / n
    for i, hand in enumerate(opponents):
        draw_card_row(
            screen, resources, hand, 
            (i + 0.5) * segment, EDGE_PADDING, 
            face_up=False, slots=HAND_SLOTS
        )