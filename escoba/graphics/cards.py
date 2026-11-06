from pathlib import Path

import pygame

from escoba.core.cards import ALL_CARDS, Card

CARD_WIDTH = 73
CARD_HEIGHT = 113

CARD_ASSET_DIR = Path(__file__).resolve().parents[2] / "assets" / "cards"


class CardRenderer:
    def __init__(self):
        # The pack numbers its faces in the same suit and rank order as ALL_CARDS.
        self.card_faces = {
            card: pygame.image.load(CARD_ASSET_DIR / f"{number}.PNG").convert_alpha()
            for number, card in enumerate(ALL_CARDS, start=1)
        }
        self.card_back = pygame.image.load(CARD_ASSET_DIR / "back.PNG").convert_alpha()

    def draw(self, screen, card: Card | None, position, face_up: bool = True):
        if face_up and card is None:
            return

        image = self.card_faces[card] if face_up else self.card_back
        screen.blit(image, position)
