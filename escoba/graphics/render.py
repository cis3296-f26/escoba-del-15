import pygame

CARD_WIDTH = 100
CARD_HEIGHT = 150

CARD_COLOR_BORDER = (17, 17, 17) #Black
CARD_COLOR_FILL = (255, 255, 255) #White

class RenderEngine:
    def __init__(self):
        self.font = pygame.font.Font()

    def draw_end_board(self, screen, state):
        # lines to display on the end board
        lines = ["Game Over", f"Winner: {state.winner()}"]
        lines += [f"{player}: {score}" for player, score in state.scores.items()]
        lines.append("Press R to play again")

        # stack the lines down the middle of the screen
        y = 20
        for line in lines:
            surface = self.font.render(line, False, CARD_COLOR_FILL)
            screen.blit(surface, surface.get_rect(centerx=screen.get_rect().centerx, top=y))
            y += 30
