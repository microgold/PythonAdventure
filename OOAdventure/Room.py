from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .UseStrategy import UseStrategyBase
from .PickStrategy import PickStrategyBase


@dataclass
class Room:
    name: str
    desc: str
    clue: Optional[str] = None
    exits: Dict[str, str] = field(
        default_factory=dict)      # direction -> room_name
    state: Dict[str, object] = field(
        default_factory=dict)   # arbitrary per-room state
    use_strategy: Optional[UseStrategyBase] = None
    pick_strategy: Optional[PickStrategyBase] = None

    def connect(self, direction: str, room_name: str) -> None:
        self.exits[direction] = room_name

    def has_exit(self, direction: str) -> bool:
        return direction in self.exits
