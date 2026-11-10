import pygame

from escoba.graphics.cards import draw_card, CARD_WIDTH, CARD_HEIGHT
from escoba.graphics.colors import YELLOW

CARD_SPACING = 8
EDGE_PADDING = 28
DECK_GAP = 24
HAND_SLOTS = 3
TABLE_SLOTS = 4

def card_row_rects(count, x, y):
    # rects for `count` cards centered on x
    total = count * CARD_WIDTH + (count - 1) * CARD_SPACING
    start = x - total / 2
    return [
        pygame.Rect(int(start + i * (CARD_WIDTH + CARD_SPACING)), int(y), CARD_WIDTH, CARD_HEIGHT)
        for i in range(count)
    ]

def draw_card_row(screen, resources, cards, x, y, face_up, slots, selected=()):
    # returns (card, rect) for every real card so clicks can find them
    cards = list(cards)
    if len(cards) < slots:
        cards = cards + [None] * (slots - len(cards))
    if not cards:
        return []

    clickable = []
    for card, rect in zip(cards, card_row_rects(len(cards), x, y)):
        draw_card(screen, resources, card, rect.topleft, face_up)
        if card is None:
            continue
        if card in selected:
            pygame.draw.rect(screen, YELLOW, rect.inflate(6, 6), width=3, border_radius=6)
        clickable.append((card, rect))

    return clickable

def draw_board(screen, resources, table_cards, player_hands, deck_count, selected=()):
    width, height = screen.get_size()
    center_x, center_y = width // 2, height // 2

    table_y = center_y - CARD_HEIGHT // 2
    table_width = TABLE_SLOTS * CARD_WIDTH + (TABLE_SLOTS - 1) * CARD_SPACING
    show_deck = deck_count > 0
    group_width = table_width + (DECK_GAP + CARD_WIDTH if show_deck else 0)
    group_left = center_x - group_width / 2

    table = draw_card_row(
        screen, resources, table_cards,
        group_left + table_width / 2, table_y,
        face_up=True, slots=TABLE_SLOTS, selected=selected
    )

    if show_deck:
        screen.blit(
            resources.card_back,
            (int(group_left + table_width + DECK_GAP), table_y)
        )

    # our own hand is face up
    hand = draw_card_row(
        screen, resources, player_hands[0], center_x,
        height - CARD_HEIGHT - EDGE_PADDING,
        face_up=True, slots=HAND_SLOTS, selected=selected
    )

    opponents = player_hands[1:]
    n = len(opponents)
    segment = width / n if n else 0
    for i, hand_cards in enumerate(opponents):
        draw_card_row(
            screen, resources, hand_cards,
            (i + 0.5) * segment, EDGE_PADDING,
            face_up=False, slots=HAND_SLOTS
        )

    return {"hand": hand, "table": table}
