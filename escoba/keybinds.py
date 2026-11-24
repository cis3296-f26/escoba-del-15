# config.ini [keybinds] stores pygame key names (K_SPACE), KEYDOWN uses event.key
from escoba.actions import Action, Input

_BIND_INPUTS = {
    "quit": Input(Action.QUIT),
    "select": Input(Action.SELECT),
    "cancel": Input(Action.CANCEL),
    "move_left": Input(Action.MOVE_LEFT),
    "move_right": Input(Action.MOVE_RIGHT),
    "move_up": Input(Action.MOVE_UP),
    "move_down": Input(Action.MOVE_DOWN),
    "move_left_arrow": Input(Action.MOVE_LEFT),
    "move_right_arrow": Input(Action.MOVE_RIGHT),
    "move_up_arrow": Input(Action.MOVE_UP),
    "move_down_arrow": Input(Action.MOVE_DOWN),
    "discard": Input(Action.DISCARD),
    "capture": Input(Action.CAPTURE)
}

class Keybinds:
    def __init__(self, by_key: dict[int, list[Input]], by_action: dict[Action, str]):
        self._by_key = by_key
        self._by_action = by_action

    def inputs(self, key: int) -> list[Input]:
        return list(self._by_key.get(key, ()))

    def label(self, action: Action) -> str:
        return self._by_action.get(action, "???")
