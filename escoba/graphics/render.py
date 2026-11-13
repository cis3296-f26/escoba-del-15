import pygame

from escoba.core.game import Game
from escoba.core.result import GameResult

from escoba.graphics.board import draw_board
from escoba.graphics.colors import WHITE, NAVY, SILVER, OLIVE

POPUP_PADDING = 32
POPUP_LINE_SPACING = 40
POPUP_TITLE_GAP = 24
POPUP_MIN_WIDTH = 460
POPUP_BORDER_RADIUS = 16

def create_window(width, height, title):
    pygame.init()
    screen = pygame.display.set_mode((width, height), pygame.SCALED)
    pygame.display.set_caption(title)
    return screen

def draw_popup(screen, resources, title, lines):
    # sized to the text, then centered on the screen
    title_surface = resources.title_font.render(title, True, WHITE)
    line_surfaces = [resources.text_font.render(line, True, WHITE) for line in lines]

    content_width = max(s.get_width() for s in [title_surface, *line_surfaces])
    popup = pygame.Rect(
        0,
        0,
        max(POPUP_MIN_WIDTH, content_width + POPUP_PADDING * 2),
        POPUP_PADDING * 2 + title_surface.get_height() + POPUP_TITLE_GAP + len(line_surfaces) * POPUP_LINE_SPACING
    )
    popup.center = screen.get_rect().center

    pygame.draw.rect(screen, NAVY, popup, border_radius=POPUP_BORDER_RADIUS)
    pygame.draw.rect(screen, SILVER, popup, width=2, border_radius=POPUP_BORDER_RADIUS)

    y = popup.top + POPUP_PADDING
    screen.blit(title_surface, title_surface.get_rect(centerx=popup.centerx, top=y))
    y += title_surface.get_height() + POPUP_TITLE_GAP

    for surface in line_surfaces:
        screen.blit(surface, surface.get_rect(centerx=popup.centerx, top=y))
        y += POPUP_LINE_SPACING

def draw(screen, resources, state, selected=None):
    # state is None (menu), Game (play), or GameResult (over)
    screen.fill(OLIVE)

    if state is None:
        draw_popup(
            screen,
            resources,
            "Escoba",
            ["Press Space to start", "Press Esc to quit"]
        )

    elif isinstance(state, Game):
        draw_board(
            screen,
            resources,
            state.table,
            [state.player_states[p.id].hand for p in state.players],
            len(state.deck),
            selected
        )

    elif isinstance(state, GameResult):
        winner = next(p for p in state.players if p.id == state.winner_id)
        scores = dict(state.scores)
        lines = [f"Winner: {winner.name}"]
        lines.extend(f"{p.name}: {scores[p.id]}" for p in state.players)
        lines.extend(["Press Space to play again", "Press N to return to menu"])
        draw_popup(screen, resources, "Game Over", lines)