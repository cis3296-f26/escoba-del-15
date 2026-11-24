import pygame

from escoba.actions import Action, Input
from escoba.graphics.colors import Color
from escoba.ui.button import Button
from escoba.ui.element import Element
from escoba.ui.layer import Layer
from escoba.ui.modal import Modal

# 1d focus step for overlay buttons (play board uses its own 2d _MOVE)
_MOVE = {
    Action.MOVE_LEFT: -1,
    Action.MOVE_RIGHT: 1,
    Action.MOVE_UP: -1,
    Action.MOVE_DOWN: 1
}

class Scene:
    bg = Color.OLIVE

    def __init__(self, ctx):
        self.ctx = ctx
        self.elements: list[Element] = []
        self.focus_i = 0

    def add(self, *elements: Element):
        self.elements.extend(elements)
        return self

    def add_overlay(self, title: str, lines: list[str], buttons: list):
        # shared modal chrome, each entry is (label, Action) or (label, Action, enabled)
        self.add(Modal(title, lines))
        screen = self.ctx.surface.get_rect()
        width, height, gap, bottom = 200, 40, 12, 48
        count = len(buttons)
        total = count * width + max(0, count - 1) * gap
        left = screen.centerx - total // 2

        for index, entry in enumerate(buttons):
            label, action = entry[0], entry[1]
            enabled = entry[2] if len(entry) > 2 else True
            button = Button(
                pygame.Rect(0, 0, width, height),
                label, enabled, action)
            button.rect.left = left + index * (width + gap)
            button.rect.bottom = screen.bottom - bottom
            button.set_goal(button.rect.topleft, snap=True)
            self.add(button)

        return self

    def focusable(self) -> list[Element]:
        return [element for element in self.elements if element.focusable and element.visible and element.enabled]

    def focused(self) -> Element | None:
        items = self.focusable()
        if not items:
            return None
        self.focus_i = max(0, min(self.focus_i, len(items) - 1))
        return items[self.focus_i]

    def hit_element(self, pos) -> Element | None:
        for element in reversed(self.elements):
            if isinstance(element, Layer):
                child = element.hit_child(pos)
                if child is not None:
                    return child
            elif element.hit(pos):
                return element
        return None

    def inputs_from_event(self, event) -> list[Input]:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            element = self.hit_element(event.pos)
            if element is not None:
                bound = element.input_at(event.pos)
                if bound is not None:
                    items = self.focusable()
                    if element in items:
                        self.focus_i = items.index(element)
                    return [bound]
        return []

    def handle_input(self, bound: Input) -> "Scene | None":
        if bound.action in _MOVE:
            items = self.focusable()
            if items:
                self.focus_i = (self.focus_i + _MOVE[bound.action]) % len(items)
            return None

        # keyboard SELECT fires whatever action the focused button owns (rematch vs menu, etc.)
        if bound.action == Action.SELECT:
            element = self.focused()
            if element is not None and getattr(element, "action", None) is not None:
                return self.on_input(Input(element.action))

        return self.on_input(bound)

    def on_input(self, bound: Input) -> "Scene | None":
        return None

    def update(self, dt: float) -> "Scene | None":
        for element in self.elements:
            element.update(dt)
        return self.on_update(dt)

    def on_update(self, dt: float) -> "Scene | None":
        return None

    def draw_elements(self, surface, *, clear=True):
        # clear=False lets popup scenes paint over an already-drawn board
        if clear:
            surface.fill(self.bg.value)

        focused = self.focused()
        for element in self.elements:
            if element.visible:
                element.draw(surface, self.ctx.resources, focused=(element is focused))

    def draw(self, surface, dt: float) -> None:
        self.draw_elements(surface, clear=True)
