import pygame

from escoba.graphics.cards import draw_card, CARD_WIDTH, CARD_HEIGHT
from escoba.graphics.colors import YELLOW

CARD_SPACING = 8
EDGE_PADDING = 28
DECK_GAP = 24
HAND_SLOTS = 3
TABLE_SLOTS = 4
SELECT_LIFT = 12
SELECT_BORDER = 3

def draw_card_row(screen, resources, cards, x, y, face_up, slots, selected=()):
    cards = list(cards)
    if len(cards) < slots:
        cards = cards + [None] * (slots - len(cards))
    if not cards:
        return

    total = len(cards) * CARD_WIDTH + (len(cards) - 1) * CARD_SPACING
    start = x - total / 2

    for i, card in enumerate(cards):
        lift = SELECT_LIFT if i in selected else 0
        pos = (int(start + i * (CARD_WIDTH + CARD_SPACING)), int(y) - lift)
        draw_card(screen, resources, card, pos, face_up)
        if i in selected:
            outline = pygame.Rect(pos, (CARD_WIDTH, CARD_HEIGHT)).inflate(SELECT_BORDER * 2, SELECT_BORDER * 2)
            pygame.draw.rect(screen, YELLOW, outline, width=SELECT_BORDER, border_radius=6)

def row_card_at(pos, count, x, y):
    # index of the card slot under pos in a row laid out like draw_card_row, or None
    total = count * CARD_WIDTH + (count - 1) * CARD_SPACING
    start = x - total / 2

    for i in range(count):
        left = int(start + i * (CARD_WIDTH + CARD_SPACING))
        if pygame.Rect(left, int(y) - SELECT_LIFT, CARD_WIDTH, CARD_HEIGHT + SELECT_LIFT).collidepoint(pos):
            return i
    return None

def table_layout(screen, deck_count):
    # (row center x, row y, group left, table width) for the table row
    width, height = screen.get_size()
    table_width = TABLE_SLOTS * CARD_WIDTH + (TABLE_SLOTS - 1) * CARD_SPACING
    group_width = table_width + (DECK_GAP + CARD_WIDTH if deck_count > 0 else 0)
    group_left = width // 2 - group_width / 2
    return group_left + table_width / 2, height // 2 - CARD_HEIGHT // 2, group_left, table_width

def hand_card_at(screen, pos):
    width, height = screen.get_size()
    return row_card_at(pos, HAND_SLOTS, width // 2, height - CARD_HEIGHT - EDGE_PADDING)

def table_card_at(screen, pos, table_count, deck_count):
    x, y, _, _ = table_layout(screen, deck_count)
    return row_card_at(pos, max(table_count, TABLE_SLOTS), x, y)

def draw_board(screen, resources, table_cards, player_hands, deck_count, selected=(), table_selected=()):
    width, height = screen.get_size()
    center_x = width // 2

    table_x, table_y, group_left, table_width = table_layout(screen, deck_count)
    show_deck = deck_count > 0

    draw_card_row(
        screen, resources, table_cards,
        table_x, table_y,
        face_up=True, slots=TABLE_SLOTS, selected=table_selected
    )

    if show_deck:
        screen.blit(
            resources.card_back,
            (int(group_left + table_width + DECK_GAP), table_y)
        )

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