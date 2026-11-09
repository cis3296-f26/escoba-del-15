from escoba.core.card import Card

CARD_WIDTH = 73
CARD_HEIGHT = 113

def draw_card(screen, resources, card: Card | None, position, face_up=True):
    image = (
        resources.card_none if card is None
        else resources.card_faces[card] if face_up
        else resources.card_back
    )
    screen.blit(image, position)