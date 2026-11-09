from escoba.graphics.cards import draw_card, CARD_WIDTH, CARD_HEIGHT

CARD_SPACING = 8
EDGE_PADDING = 28
DECK_GAP = 24
HAND_SLOTS = 3
TABLE_SLOTS = 4

def draw_card_row(screen, resources, cards, x, y, face_up, slots):
    cards = list(cards)
    if len(cards) < slots:
        cards = cards + [None] * (slots - len(cards))
    if not cards:
        return

    total = len(cards) * CARD_WIDTH + (len(cards) - 1) * CARD_SPACING
    start = x - total / 2

    for i, card in enumerate(cards):
        pos = (int(start + i * (CARD_WIDTH + CARD_SPACING)), int(y))
        draw_card(screen, resources, card, pos, face_up)

def draw_board(screen, resources, table_cards, player_hands, deck_count):
    width, height = screen.get_size()
    center_x, center_y = width // 2, height // 2

    table_y = center_y - CARD_HEIGHT // 2
    table_width = TABLE_SLOTS * CARD_WIDTH + (TABLE_SLOTS - 1) * CARD_SPACING
    show_deck = deck_count > 0
    group_width = table_width + (DECK_GAP + CARD_WIDTH if show_deck else 0)
    group_left = center_x - group_width / 2

    draw_card_row(
        screen, resources, table_cards,
        group_left + table_width / 2, table_y,
        face_up=True, slots=TABLE_SLOTS
    )

    if show_deck:
        screen.blit(
            resources.card_back,
            (int(group_left + table_width + DECK_GAP), table_y)
        )

    draw_card_row(
        screen, resources, player_hands[0], center_x,
        height - CARD_HEIGHT - EDGE_PADDING,
        face_up=False, slots=HAND_SLOTS
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