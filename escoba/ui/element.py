import pygame

from escoba.actions import Input
from escoba.graphics.colors import Color

def panel(surface, rect, fill=Color.NAVY, border=Color.SILVER, radius=16, border_width=2, alpha=255):
    if alpha >= 255:
        pygame.draw.rect(surface, fill.value, rect, border_radius=radius)
        pygame.draw.rect(surface, border.value, rect, width=border_width, border_radius=radius)
        return

    # draw translucent chrome offscreen so callers can still blit opaque text on top
    buffer = pygame.Surface(rect.size, pygame.SRCALPHA)
    box = buffer.get_rect()
    pygame.draw.rect(buffer, (*fill.value[:3], alpha), box, border_radius=radius)
    pygame.draw.rect(buffer, (*border.value[:3], alpha), box, width=border_width, border_radius=radius)
    surface.blit(buffer, rect.topleft)

def outline(surface, rect, color=Color.WHITE, width=2, inflate=6, radius=8):
    pygame.draw.rect(
        surface, color.value, rect.inflate(inflate, inflate),
        width=width, border_radius=radius)

class Element:
    def __init__(self, rect: pygame.Rect | None = None, *,
                 visible=True, enabled=True, focusable=False):
        self.rect = pygame.Rect(rect) if rect is not None else pygame.Rect(0, 0, 0, 0)
        self.visible = visible
        self.enabled = enabled
        self.focusable = focusable
        self.goal = self.rect.topleft
        self.tag = None
        self._pos = [float(self.rect.x), float(self.rect.y)]

    @property
    def idle(self) -> bool:
        # close enough to the goal that the next action can run
        return abs(self._pos[0] - self.goal[0]) <= 0.5 and abs(self._pos[1] - self.goal[1]) <= 0.5

    def set_goal(self, pos, *, snap=False):
        self.goal = (int(pos[0]), int(pos[1]))
        if snap:
            self.snap()

    def snap(self):
        self._pos = [float(self.goal[0]), float(self.goal[1])]
        self.rect.topleft = self.goal

    def update(self, dt: float):
        # lerp toward goal at ~1000 px/s (presentation only)
        gx, gy = self.goal
        dx, dy = gx - self._pos[0], gy - self._pos[1]
        dist = (dx * dx + dy * dy) ** 0.5

        if dist > 0.5:
            step = 1000.0 * dt
            if step >= dist:
                self._pos = [float(gx), float(gy)]
            else:
                self._pos[0] += dx / dist * step
                self._pos[1] += dy / dist * step
            self.rect.topleft = (int(self._pos[0]), int(self._pos[1]))
        else:
            self.rect.topleft = self.goal
            self._pos = [float(gx), float(gy)]

    def hit(self, pos) -> bool:
        return self.visible and self.enabled and self.rect.collidepoint(pos)

    def input_at(self, pos) -> Input | None:
        return None

    def draw(self, surface, resources, focused: bool = False):
        pass
