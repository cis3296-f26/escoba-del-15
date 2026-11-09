# frozen player identity only

from dataclasses import dataclass

@dataclass(frozen=True)
class Player:
    id: int
    name: str
    is_cpu: bool = False