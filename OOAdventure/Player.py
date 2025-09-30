from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Player:
    room: str = "Entrance"
    inventory: List[str] = field(default_factory=list)

    def has(self, item_name: str) -> bool:
        return item_name in self.inventory

    def add(self, item_name: str) -> None:
        if item_name not in self.inventory:
            self.inventory.append(item_name)

    def remove(self, item_name: str) -> None:
        if item_name in self.inventory:
            self.inventory.remove(item_name)
