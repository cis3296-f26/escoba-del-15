import pygame

from escoba.core.card import Card
from escoba.ui.label import Label

CARD_WIDTH = 73
CARD_HEIGHT = 113
SELECT_LIFT = 6  # selected cards rise this many px

class CardSprite(Label):
    # Label that shows a card face, back, or empty slot from resources
    def __init__(self, card: Card | None, slot: pygame.Rect, *,
                 face_up=True, selected=False, zone="", index=0,
                 focusable=True, enabled=True, force_back=False):
        super().__init__(
            pygame.Rect(slot.x, slot.y, CARD_WIDTH, CARD_HEIGHT),
            focusable=False, enabled=True)
        self.zone = zone
        self.index = index
        self.apply(card, slot, face_up=face_up, selected=selected,
                   focusable=focusable, enabled=enabled, force_back=force_back, snap=True)

    def apply(self, card: Card | None, slot: pygame.Rect, *,
              face_up=True, selected=False, focusable=True, enabled=True,
              force_back=False, snap=False):
        # first create snaps, later syncs lerp to the new slot / lift
        interactive = (not force_back) and card is not None and focusable
        self.card = card
        self.face_up = face_up
        self.force_back = force_back
        self.place(
            pygame.Rect(slot.x, slot.y, CARD_WIDTH, CARD_HEIGHT),
            selected=selected, lift=SELECT_LIFT,
            focusable=interactive, enabled=enabled and interactive, snap=snap)

    def draw(self, surface, resources, focused: bool = False):
        if self.force_back:
            self.image = resources.card_back
        elif self.card is None:
            self.image = resources.card_empty
        elif self.face_up:
            self.image = resources.card_faces[self.card]
        else:
            self.image = resources.card_back
        super().draw(surface, resources, focused=focused)
