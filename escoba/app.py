from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path

import pygame

from escoba.actions import Action, Input
from escoba.core.player import Player
from escoba.graphics.resources import Resources
from escoba.keybinds import Keybinds, _BIND_INPUTS
from escoba.language import Language
from escoba.scenes.overlays import MenuScene

CONFIG_PATH = Path(__file__).resolve().parent / "assets" / "config.ini"

@dataclass
class Context:
    surface: pygame.Surface
    resources: Resources
    text: Language
    binds: Keybinds
    players: tuple[Player, ...]

def load_config() -> tuple[Keybinds, str]:
    # config.ini holds both keybinds and the language code
    parser = ConfigParser()
    parser.read(CONFIG_PATH, encoding="utf-8")

    language = "en"
    if parser.has_section("general"):
        language = parser.get("general", "language", fallback="en").strip() or "en"

    by_key: dict[int, list[Input]] = {}
    by_action: dict[Action, str] = {}

    if parser.has_section("keybinds"):
        for name, value in parser.items("keybinds"):
            bound = _BIND_INPUTS.get(name)
            if bound is None:
                continue

            key_name = value.strip()
            keycode = getattr(pygame, key_name, None)
            if not isinstance(keycode, int):
                continue

            label = key_name[2:].replace("_", " ").title() if key_name.startswith("K_") else key_name
            by_key.setdefault(keycode, []).append(bound)
            by_action.setdefault(bound.action, label)

    return Keybinds(by_key, by_action), language

def create_window(width, height, title):
    pygame.init()
    screen = pygame.display.set_mode((width, height), pygame.SCALED)
    pygame.display.set_caption(title)
    return screen

class App:
    def __init__(self):
        binds, lang_code = load_config()
        text = Language.load(lang_code)
        surface = create_window(960, 640, text("window_title"))

        self.ctx = Context(surface, Resources(binds), text, binds, (
            Player(0, text("player_you")),
            Player(1, text("player_cpu", n=1), is_cpu=True),
            Player(2, text("player_cpu", n=2), is_cpu=True)
        ))
        self.scene = MenuScene(self.ctx)
        self._clock = pygame.time.Clock()
        self._running = True

    def set_scene(self, scene):
        if scene is not None:
            self.scene = scene

    def run(self):
        ctx = self.ctx

        while self._running:
            dt = self._clock.tick(30) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                    break

                if event.type == pygame.KEYDOWN:
                    for bound in ctx.binds.inputs(event.key):
                        if bound.action == Action.QUIT:
                            self._running = False
                            break
                        self.set_scene(self.scene.handle_input(bound))
                    continue

                for bound in self.scene.inputs_from_event(event):
                    self.set_scene(self.scene.handle_input(bound))

            if not self._running:
                break

            self.set_scene(self.scene.update(dt))
            self.scene.draw(ctx.surface, dt)
            pygame.display.flip()

        pygame.quit()
