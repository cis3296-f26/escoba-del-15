import pygame

from escoba.actions import Action
from escoba.graphics.card_sprite import CARD_HEIGHT, CARD_WIDTH, CardSprite, SELECT_LIFT
from escoba.ui.button import Button
from escoba.ui.label import Label

def row_lefts(count, x, max_width=None):
    # shrink the gap when the row would overflow max_width
    spacing = 8
    step = CARD_WIDTH + spacing
    total = count * CARD_WIDTH + (count - 1) * spacing

    if max_width is not None and total > max_width and count > 1:
        step = (max_width - CARD_WIDTH) / (count - 1)
        total = max_width

    start = x - total / 2
    return [int(start + i * step) for i in range(count)]

def table_layout(screen):
    width, height = screen.get_size()
    pad, deck_gap = 28, 24
    center_x = width // 2
    deck_x = width - pad - CARD_WIDTH
    max_width = 2 * min(center_x - pad, deck_x - deck_gap - center_x)
    return center_x, height // 2 - CARD_HEIGHT // 2, max_width, deck_x

def action_button_rects(screen):
    # bottom edge, under the local hand
    width, height = screen.get_size()
    button_w, button_h, gap, pad = 160, 32, 12, 16
    total = button_w * 2 + gap
    left = width // 2 - total // 2
    top = height - pad - button_h

    discard = pygame.Rect(left, top, button_w, button_h)
    capture = pygame.Rect(discard.right + gap, top, button_w, button_h)
    return discard, capture

def seat_layouts(screen, player_count):
    # you at the bottom, every opponent shares the top row evenly
    width, height = screen.get_size()
    pad = 28
    name_gap = 22
    hand_span = 3 * CARD_WIDTH + 2 * 8
    gap = 16
    button_h = 32

    south_hand_y = height - pad - button_h - gap - SELECT_LIFT - CARD_HEIGHT
    south_hand_x = width // 2
    seats = [{
        "hand_x": south_hand_x,
        "hand_y": south_hand_y,
        "hand_max": hand_span,
        "pile": pygame.Rect(
            south_hand_x - hand_span // 2 - gap - CARD_WIDTH,
            south_hand_y, CARD_WIDTH, CARD_HEIGHT),
        "hand_face_up": True,
        "pile_face_up": True,
        "zone": "hand"
    }]

    opponents = max(0, player_count - 1)
    if opponents == 0:
        return seats

    top_y = pad + name_gap
    # hand + pile as one block, centered in each equal top column
    block = hand_span + gap + CARD_WIDTH
    column = (width - 2 * pad) / opponents

    for index in range(opponents):
        center = pad + column * (index + 0.5)
        left = int(center - block / 2)
        hand_x = left + hand_span // 2
        seats.append({
            "hand_x": hand_x,
            "hand_y": top_y,
            "hand_max": min(hand_span, int(column) - CARD_WIDTH - gap),
            "pile": pygame.Rect(left + hand_span + gap, top_y, CARD_WIDTH, CARD_HEIGHT),
            "hand_face_up": False,
            "pile_face_up": False,
            "zone": f"opponent-{index}"
        })

    return seats

def _card_item(tag, card, slot, *, face_up, selected, zone, index,
               focusable=True, enabled=True, force_back=False, spawn_slot=None, snap_apply=False):
    # (tag, create, apply) for Layer.sync — create once, apply every frame
    def create():
        origin = spawn_slot if spawn_slot is not None else slot
        return CardSprite(
            card, origin, face_up=face_up, selected=selected, zone=zone,
            index=index, focusable=focusable, enabled=enabled, force_back=force_back)

    def apply(sprite: CardSprite):
        sprite.zone = zone
        sprite.index = index
        sprite.apply(
            card, slot, face_up=face_up, selected=selected,
            focusable=focusable, enabled=enabled, force_back=force_back, snap=snap_apply)

    return tag, create, apply

def _button_item(tag, rect, label, enabled, action):
    def create():
        button = Button(rect, label, enabled, action)
        button.tag = tag
        button.set_goal(rect.topleft, snap=True)
        return button

    def apply(button: Button):
        button.label = label
        button.enabled = enabled
        button.focusable = enabled
        button.action = action
        button.rect.size = (rect.width, rect.height)
        button.set_goal(rect.topleft)

    return tag, create, apply

def _name_item(tag, text, midbottom):
    def create():
        label = Label(text=text, midbottom=midbottom)
        label.tag = tag
        return label

    def apply(label: Label):
        label.text = text
        label.midbottom = midbottom

    return tag, create, apply

def _row_items(cards, x, y, face_up, slots, zone, selected=(), max_width=None, spawn_slot=None):
    # empty pads keep row width stable while real cards travel
    cards = list(cards)
    empties = max(0, slots - len(cards))
    total = len(cards) + empties
    if total == 0:
        return []

    lefts = row_lefts(total, x, max_width)
    items = []

    for index, card in enumerate(cards):
        slot = pygame.Rect(lefts[index], int(y), CARD_WIDTH, CARD_HEIGHT)
        interactive = zone in ("hand", "table")
        items.append(_card_item(
            ("card", card), card, slot, face_up=face_up, selected=index in selected,
            zone=zone, index=index, focusable=interactive, enabled=interactive,
            spawn_slot=spawn_slot))

    for index in range(len(cards), total):
        slot = pygame.Rect(lefts[index], int(y), CARD_WIDTH, CARD_HEIGHT)
        items.append(_card_item(
            ("empty", zone, index), None, slot, face_up=True, selected=False,
            zone=zone, index=index, focusable=False, enabled=False, snap_apply=True))

    return items

def _stack_slots(slot, count, depth=3):
    # small diagonal cascade, capped so big piles stay compact
    shown = min(depth, count)
    return [
        pygame.Rect(slot.x + index * 3, slot.y + index * 3, CARD_WIDTH, CARD_HEIGHT)
        for index in range(shown)
    ]

def _pile_items(captured, slot, zone, face_up=True):
    shown = list(captured)[-3:]
    return [
        _card_item(
            ("card", card), card, stacked, face_up=face_up, selected=False,
            zone=zone, index=index, focusable=False, enabled=False, spawn_slot=slot)
        for index, (card, stacked) in enumerate(zip(shown, _stack_slots(slot, len(shown))))
    ]

def _deck_items(deck_count, slot):
    items = []
    for index, stacked in enumerate(_stack_slots(slot, deck_count)):
        items.append(_card_item(
            ("deck", index), None, stacked, face_up=False, selected=False,
            zone="deck", index=index, focusable=False, enabled=False,
            force_back=True, snap_apply=True))
    return items

def board_items(screen, table_cards, player_hands, player_captured, deck_count,
                hand_selected=(), table_selected=(),
                *, player_names=(), discard_label="", capture_label="",
                discard_on=False, capture_on=False, show_buttons=False):
    table_x, table_y, table_max_width, deck_x = table_layout(screen)
    deck_rect = pygame.Rect(deck_x, table_y, CARD_WIDTH, CARD_HEIGHT)
    seats = seat_layouts(screen, len(player_hands))
    items = []

    items.extend(_row_items(
        table_cards, table_x, table_y, True, 4, "table",
        selected=table_selected, max_width=table_max_width, spawn_slot=deck_rect))

    items.extend(_deck_items(deck_count, deck_rect))

    for player_index, seat in enumerate(seats):
        selected = hand_selected if player_index == 0 else ()
        items.extend(_row_items(
            player_hands[player_index], seat["hand_x"], seat["hand_y"],
            seat["hand_face_up"], 3, seat["zone"], selected=selected,
            max_width=seat["hand_max"], spawn_slot=deck_rect))
        items.extend(_pile_items(
            player_captured[player_index], seat["pile"], f"pile-{player_index}",
            face_up=seat["pile_face_up"]))

        if player_index > 0 and player_index < len(player_names):
            items.append(_name_item(
                ("name", player_index),
                player_names[player_index],
                (seat["hand_x"], seat["hand_y"] - 6)))

    if show_buttons:
        discard_rect, capture_rect = action_button_rects(screen)
        items.append(_button_item(("buttons", 0), discard_rect, discard_label, discard_on, Action.DISCARD))
        items.append(_button_item(("buttons", 1), capture_rect, capture_label, capture_on, Action.CAPTURE))

    return items
