from pathlib import Path

import pygame

from escoba.core.card import ALL_CARDS

CARD_ASSET_DIR = Path(__file__).resolve().parent.parent / "assets" / "cards"

class Resources:
    def __init__(self):
        self.text_font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 64)
        self.button_font = pygame.font.Font(None, 24)
        
        self.card_faces = {
            card: pygame.image.load(CARD_ASSET_DIR / f"{card.suit.value}_{card.rank}.png").convert_alpha()
                for card in ALL_CARDS
        }
        self.card_back = pygame.image.load(CARD_ASSET_DIR / "back.png").convert_alpha() 
        self.card_none = pygame.image.load(CARD_ASSET_DIR / "empty.png").convert_alpha()