from itertools import zip_longest

import pygame

from escoba.graphics.cards import draw_card, CARD_WIDTH, CARD_HEIGHT

CARD_SPACING = 8
CAPTURE_STACK_SPACING = 4
CAPTURE_STACK_LAYERS = 6  # the pile stops spreading after this many cards
EDGE_PADDING = 28
DECK_GAP = 24
HAND_SLOTS = 3
TABLE_SLOTS = 4
SELECTION_COLOR = (255, 215, 92)

# layout, shared by drawing, click hit-testing and move animations

def card_row(center_x, y, places, step=CARD_WIDTH + CARD_SPACING):
    start = center_x - (CARD_WIDTH + (places - 1) * step) / 2
    return [
        pygame.Rect(int(start + i * step), int(y), CARD_WIDTH, CARD_HEIGHT)
        for i in range(places)
    ]

def player_area(bounds, index, player_count):
    # player 0 gets the bottom edge; opponents split the top edge evenly
    if index == 0:
        return pygame.Rect(bounds.left, bounds.bottom - CARD_HEIGHT - EDGE_PADDING, bounds.width, CARD_HEIGHT)
    width = bounds.width // (player_count - 1)
    return pygame.Rect(bounds.left + (index - 1) * width, bounds.top + EDGE_PADDING, width, CARD_HEIGHT)

def hand_rects(bounds, index, player_count, count):
    area = player_area(bounds, index, player_count)
    return card_row(area.centerx, area.y, max(count, HAND_SLOTS))

def capture_stack_position(bounds, index, player_count, stack_index):
    # face-down pile at the right end of each player's area; it grows leftward up to
    # CAPTURE_STACK_LAYERS cards, then new cards land on top so it never reaches the hand
    area = player_area(bounds, index, player_count)
    layer = min(stack_index, CAPTURE_STACK_LAYERS - 1)
    return area.right - EDGE_PADDING - CARD_WIDTH - layer * CAPTURE_STACK_SPACING, area.y

def table_rects(bounds, count, deck_count):
    # the table row and the deck are centered together as one group;
    # a long table squeezes its cards together so the group stays on screen
    places = max(count, TABLE_SLOTS)
    deck_width = DECK_GAP + CARD_WIDTH if deck_count else 0
    room = bounds.width - 2 * EDGE_PADDING - deck_width
    step = min(CARD_WIDTH + CARD_SPACING, (room - CARD_WIDTH) // (places - 1))
    return card_row(bounds.centerx - deck_width / 2, bounds.centery - CARD_HEIGHT // 2, places, step=step)

def move_button(bounds):
    button = pygame.Rect(0, 0, 112, 34)
    button.center = (bounds.centerx, bounds.bottom - CARD_HEIGHT - EDGE_PADDING - 36)
    return button

# drawing

def draw_card_row(screen, resources, cards, rects, face_up, selected, hidden):
    # places past the last card, and cards mid-animation, draw as empty slots
    for card, rect in zip_longest(cards, rects):
        if card in hidden:
            card = None
        draw_card(screen, resources, card, rect.topleft, face_up)
        if card is not None and card in selected:
            pygame.draw.rect(screen, SELECTION_COLOR, rect, width=3)

def draw_board(screen, resources, game, selected, hidden):
    bounds = screen.get_rect()
    player_count = len(game.players)
    deck_count = len(game.deck)

    table = table_rects(bounds, len(game.table), deck_count)
    draw_card_row(screen, resources, game.table, table, True, selected, hidden)

    if deck_count:
        screen.blit(resources.card_back, (table[-1].right + DECK_GAP, table[-1].y))

    for i, player in enumerate(game.players):
        state = game.player_states[player.id]
        rects = hand_rects(bounds, i, player_count, len(state.hand))
        # only the human player's own hand is face up
        draw_card_row(screen, resources, state.hand, rects, i == 0, selected, hidden)
        for stack_index in range(min(state.capture_count, CAPTURE_STACK_LAYERS)):
            screen.blit(resources.card_back, capture_stack_position(bounds, i, player_count, stack_index))
