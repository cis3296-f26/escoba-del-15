import pygame

from escoba.graphics.colors import WHITE, NAVY, SILVER

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
