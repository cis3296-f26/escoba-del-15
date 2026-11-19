import pygame

from escoba.graphics.colors import Color
from escoba.ui.element import Element, outline

class Label(Element):
    # static content: text, image, or both
    def __init__(self, rect: pygame.Rect | None = None, *,
                 text: str | None = None, image=None, midbottom=None,
                 selected=False, focusable=False, enabled=True):
        super().__init__(rect, focusable=focusable, enabled=enabled)
        self.text = text
        self.image = image
        self.midbottom = midbottom
        self.selected = selected

    def place(self, slot: pygame.Rect, *, selected=False, lift=0,
              focusable=None, enabled=None, snap=False):
        if focusable is not None:
            self.focusable = focusable
        if enabled is not None:
            self.enabled = enabled
        self.selected = selected
        self.rect.size = (slot.width, slot.height)
        y = slot.y - lift if selected else slot.y
        self.set_goal((slot.x, y), snap=snap)

    def draw(self, surface, resources, focused: bool = False):
        if not self.visible:
            return

        if self.image is not None:
            surface.blit(self.image, self.rect.topleft)

        if self.text:
            rendered = resources.text_font.render(self.text, True, Color.WHITE.value)
            if self.image is None and self.midbottom is not None:
                self.rect = rendered.get_rect(midbottom=self.midbottom)
                surface.blit(rendered, self.rect)
            else:
                surface.blit(rendered, rendered.get_rect(center=self.rect.center))

        if self.selected:
            outline(surface, self.rect, Color.ORANGE, width=3, inflate=6, radius=6)
        if focused:
            outline(surface, self.rect, Color.WHITE, width=2, inflate=8, radius=6)
