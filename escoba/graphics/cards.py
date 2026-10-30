import pygame

from escoba.core.cards import Card, ALL_CARDS

CARD_WIDTH = 50
CARD_HEIGHT = 80

CARD_CORNER_RADIUS = 8
CARD_BORDER_WIDTH = 2

CARD_COLOR_BORDER = (17, 17, 17) #Black
CARD_COLOR_FILL = (255, 255, 255) #White
CARD_COLOR_TEXT = (170, 170, 170) #Gray
CARD_COLOR_NONE = (127, 219, 255) #Aqua

class CardRenderer:
    def __init__(self):
        self.font = pygame.font.Font(None, 20)
        # pre-render and cache every card
        self.card_faces = { card: self._create_card(card) for card in ALL_CARDS }
        self.card_back = self._create_card(None)
        self.card_none = self._create_card_none()

    def _create_card(self, card: Card):
        surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)

        pygame.draw.rect(
            surface, 
            CARD_COLOR_FILL, 
            (0, 0, CARD_WIDTH, CARD_HEIGHT),
            border_radius=CARD_CORNER_RADIUS
            )

        pygame.draw.rect(
            surface, 
            CARD_COLOR_BORDER, 
            (0, 0, CARD_WIDTH, CARD_HEIGHT),
            width=CARD_BORDER_WIDTH,
            border_radius=CARD_CORNER_RADIUS
            )

        if card is not None:
            rank = self.font.render(str(card.rank), True, CARD_COLOR_TEXT)
            surface.blit(rank, (4, 4))
            
            suit = self.font.render(card.suit.value, True, CARD_COLOR_TEXT)
            surface.blit(suit, (4, 24))
        
        return surface.convert_alpha()

    def _create_card_none(self):
        surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)

        pygame.draw.rect(
            surface, 
            CARD_COLOR_NONE, 
            (0, 0, CARD_WIDTH, CARD_HEIGHT),
            width=CARD_BORDER_WIDTH,
            border_radius=CARD_CORNER_RADIUS
            )
        
        return surface.convert_alpha()

    def draw(self, screen, card: Card | None, position, face_up: bool = True):
        if card is None and not __debug__: 
            return

        surface = (
            self.card_none if card is None
            else self.card_faces[card] if face_up 
            else self.card_back
            )
        
        screen.blit(surface, position)