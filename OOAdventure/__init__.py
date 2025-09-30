# OOAdventure/__init__.py

# Expose main classes at the package level
from .Game import Game
from .Room import Room
from .Player import Player
from .Item import Item

# You can also expose base strategy classes
from .UseStrategy import UseStrategyBase
from .PickStrategy import PickStrategyBase

# Optional: expose specific strategies if you want them easy to import
from .UseStrategy.LibraryUse import LibraryUse
from .UseStrategy.AltarUse import AltarUse
from .UseStrategy.ChamberUse import ChamberUse
from .UseStrategy.VaultUse import VaultUse

from .PickStrategy.ChamberPick import ChamberPick

# Define what `from OOAdventure import *` gives you
__all__ = [
    "Game",
    "Room",
    "Player",
    "Item",
    "UseStrategyBase",
    "PickStrategyBase",
    "LibraryUse",
    "AltarUse",
    "ChamberUse",
    "VaultUse",
    "ChamberPick",
]
