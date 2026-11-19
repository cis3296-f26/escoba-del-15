import pygame

from escoba.actions import Action, Input
from escoba.graphics.colors import Color
from escoba.ui.element import Element, outline

class Button(Element):
    def __init__(self, rect: pygame.Rect, label: str, enabled: bool = True,
                 action: Action | None = None, *, focusable: bool = True):
        super().__init__(rect, enabled=enabled, focusable=focusable and enabled)
        self.label = label
        self.action = action

    def input_at(self, pos) -> Input | None:
        if self.action is not None and self.hit(pos):
            return Input(self.action)
        return None

    def caption(self, resources) -> str:
        if self.action is None or resources.binds is None:
            return self.label
        return f"{self.label} ({resources.binds.label(self.action)})"

    def draw(self, surface, resources, focused: bool = False):
        if not self.visible:
            return

        fill, ink = (Color.WHITE, Color.BLACK) if self.enabled else (Color.SILVER, Color.GRAY)
        pygame.draw.rect(surface, fill.value, self.rect, border_radius=6)
        pygame.draw.rect(surface, ink.value, self.rect, width=2, border_radius=6)

        if focused:
            outline(surface, self.rect, Color.WHITE, width=2, inflate=6, radius=8)

        text = resources.button_font.render(self.caption(resources), True, ink.value)
        max_w = max(1, self.rect.width - 12)
        if text.get_width() > max_w:
            height = max(1, int(text.get_height() * max_w / text.get_width()))
            text = pygame.transform.smoothscale(text, (max_w, height))
        surface.blit(text, text.get_rect(center=self.rect.center))
