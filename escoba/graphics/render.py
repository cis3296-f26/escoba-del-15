import pygame

from escoba.core.game import Game, GameState

from escoba.graphics.board import BoardRenderer

CARD_WIDTH = 100
CARD_HEIGHT = 150

CARD_COLOR_BORDER = (17, 17, 17) #Black
CARD_COLOR_FILL = (255, 255, 255) #White

TABLE_COLOR = (61, 153, 112) #Olive

class RenderEngine:
    def __init__(self):
        self.text_font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 64)

        self.board_renderer = BoardRenderer()

    def draw(self, screen, game):
        if game.state == GameState.START:
            self.draw_start(screen)
        elif game.state == GameState.PLAY:
            self.draw_play(screen, game)
        elif game.state == GameState.GAME_OVER:
            self.draw_game_over(screen, game)

    # draw title screen and new game buttons
    def draw_start(self, screen):
        screen.fill(TABLE_COLOR)

        # draw game title
        title = self.title_font.render("Escoba", True, CARD_COLOR_FILL)
        screen.blit(
            title,
            title.get_rect(
                centerx=screen.get_rect().centerx, 
                centery=screen.get_rect().centery - 100 
            )
        )

        text = self.text_font.render("Press Enter to start", True, CARD_COLOR_FILL)
        screen.blit(
            text,
            text.get_rect(
                centerx=screen.get_rect().centerx,
                centery=screen.get_rect().centery + 100
            )
        )

    # draw the play screen
    def draw_play(self, screen, game):
            self.board_renderer.draw(
                screen, 
                game.table, 
                [player.hand for player in game.players], 
                len(game.deck))

    # draw winner, scores and new game buttons 
    def draw_game_over(self, screen, game):
        screen.fill(TABLE_COLOR)

        # lines to display on the end board
        lines = ["Game Over", f"Winner: {game.winner()}"]
        lines += [f"{player}: {score}" for player, score in game.scores.items()]
        lines.append("Press R to play again")

        y = screen.get_rect().centery - (len(lines) * 40) // 2

        # stack the lines down the middle of the screen

        for line in lines:
            surface = self.text_font.render(line, False, CARD_COLOR_FILL)
            screen.blit(
                surface, 
                surface.get_rect(
                    centerx=screen.get_rect().centerx, 
                    top=y
                )
            )
            y += 40
