import pygame

from escoba.graphics.colors import Color
from escoba.ui.element import Element, panel

class Modal(Element):
    def __init__(self, title: str, lines: list[str], *, center=None):
        super().__init__(focusable=False)
        self.title = title
        self.lines = list(lines)
        self._center = center

    def layout(self, surface, resources):
        pad, title_gap, line_gap = 32, 24, 40
        title_s = resources.title_font.render(self.title, True, Color.WHITE.value)
        line_surfaces = [resources.text_font.render(line, True, Color.WHITE.value) for line in self.lines]

        content_width = title_s.get_width()
        if line_surfaces:
            content_width = max(content_width, max(s.get_width() for s in line_surfaces))

        height = pad * 2 + title_s.get_height()
        if line_surfaces:
            height += title_gap + len(line_surfaces) * line_gap

        box = pygame.Rect(0, 0, max(460, content_width + pad * 2), height)
        box.center = self._center or surface.get_rect().center
        self.rect = box
        self.set_goal(box.topleft, snap=True)
        return title_s, line_surfaces, pad, title_gap, line_gap

    def draw(self, surface, resources, focused: bool = False):
        if not self.visible:
            return

        title_s, line_surfaces, pad, title_gap, line_gap = self.layout(surface, resources)
        # ~90% opaque chrome, text blits fully opaque on top
        panel(surface, self.rect, radius=16, alpha=230)

        y = self.rect.top + pad
        surface.blit(title_s, title_s.get_rect(centerx=self.rect.centerx, top=y))
        y += title_s.get_height() + title_gap

        for line_s in line_surfaces:
            surface.blit(line_s, line_s.get_rect(centerx=self.rect.centerx, top=y))
            y += line_gap
