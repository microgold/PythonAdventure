from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Item:
    name: str
    location: Optional[str]                 # room name | "inventory" | None
    used_in: Optional[str] = None
    aliases: List[str] = field(default_factory=list)
