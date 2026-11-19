# what the player wants — not which key was pressed
# keyboard, clicks, and tests all build Input the same way
from dataclasses import dataclass
from enum import Enum

class Action(Enum):
    QUIT = "quit"
    SELECT = "select"
    CANCEL = "cancel"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down"
    DISCARD = "discard"
    CAPTURE = "capture"

@dataclass(frozen=True)
class Input:
    action: Action