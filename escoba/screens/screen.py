from typing import Protocol

import pygame


class Screen(Protocol):
    def handle_event(self, event: pygame.event.Event) -> None: ...

    def draw(self, surface: pygame.Surface) -> None: ...
