#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import Dict, List, Optional

# ----------------------------
# Core domain objects
# ----------------------------


@dataclass
class Item:
    name: str
    # room name or "inventory" or None (not yet placed)
    location: Optional[str]
    used_in: Optional[str] = None  # hint/metadata; not enforced automatically


@dataclass
class Room:
    name: str
    desc: str
    clue: Optional[str] = None
    exits: Dict[str, str] = field(
        default_factory=dict)  # direction -> room_name
    state: Dict[str, str] = field(
        default_factory=dict)  # arbitrary per-room state

    def connect(self, direction: str, room_name: str) -> None:
        """Add a directional exit."""
        self.exits[direction] = room_name

    def has_exit(self, direction: str) -> bool:
        return direction in self.exits


@dataclass
class Player:
    room: str  # room name
    inventory: List[str] = field(default_factory=list)  # list of item names

    def has(self, item_name: str) -> bool:
        return item_name in self.inventory

    def add(self, item_name: str) -> None:
        if item_name not in self.inventory:
            self.inventory.append(item_name)

    def remove(self, item_name: str) -> None:
        if item_name in self.inventory:
            self.inventory.remove(item_name)


# ----------------------------
# The Game controller
# ----------------------------

class Game:
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.items: Dict[str, Item] = {}
        self.player = Player(room="Entrance")

        # Aliases & parser tables
        self.DIR_ALIASES = {
            "n": "north", "s": "south", "e": "east", "w": "west",
            "north": "north", "south": "south", "east": "east", "west": "west"
        }
        self.VERB_ALIASES = {
            "go": "go", "move": "go", "walk": "go",
            "pick": "pick", "take": "pick", "get": "pick", "grab": "pick",
            "use": "use",
            "look": "look", "l": "look", "examine": "look",
            "inventory": "inventory", "i": "inventory",
            "help": "help", "quit": "quit", "exit": "quit"
        }
        self.COMMANDS = {
            "go": self.handle_go,
            "pick": self.handle_pick,
            "use": self.handle_use,
            "look": self.handle_look,
            "inventory": self.handle_inventory,
            "help": self.handle_help,
            "quit": self.handle_quit
        }

        self._build_world()

    # ---------- World setup ----------

    def _build_world(self):
        # Rooms
        self.rooms["Entrance"] = Room(
            name="Entrance",
            desc="You stand at the grand entrance of the ancient tower."
        )
        self.rooms["Library"] = Room(
            name="Library",
            desc="Dusty books line the walls. A faint glow comes from a pedestal.",
            clue="A crystal orb must be placed on the pedestal to reveal the path east."
        )
        self.rooms["Altar"] = Room(
            name="Altar",
            desc="An altar with runes that pulse softly. A deep chasm blocks the northern path.",
            clue="You need an enchanted rope to cross the chasm below."
        )
        self.rooms["Chamber"] = Room(
            name="Chamber",
            desc="The chamber contains a frozen pool. Something glitters beneath the ice.",
            clue="Perhaps fire could melt the ice, and cold could make it safe again.",
            state={"ice_state": "frozen"}  # frozen -> melted -> refrozen
        )
        self.rooms["Vault"] = Room(
            name="Vault",
            desc="A vault door bars your way. The Gem of Eternity sits on a stone altar inside.",
            clue="You need the teleportation stone (and a key) to open this vault from here.",
            state={"open": "false"}  # start closed
        )
        # Initial exits (locked exits are omitted until unlocked)
        self.rooms["Entrance"].connect("north", "Library")
        self.rooms["Library"].connect("south", "Entrance")
        self.rooms["Altar"].connect("west", "Library")
        self.rooms["Chamber"].connect("south", "Altar")
        self.rooms["Vault"].connect("west", "Chamber")
        # NOTE: Library->east and Altar->north and Chamber->east are gated by puzzles.

        # Items
        self.items["Crystal Orb"] = Item(
            "Crystal Orb", "Library", used_in="Library")
        self.items["Enchanted Rope"] = Item(
            "Enchanted Rope", "Altar", used_in="Chasm")
        self.items["Fire Scroll"] = Item(
            "Fire Scroll", "Chamber", used_in="Ice Pool")
        self.items["Ice Wand"] = Item(
            "Ice Wand", "Chamber", used_in="Ice Pool")
        self.items["Teleportation Stone"] = Item(
            "Teleportation Stone", "Entrance", used_in="Vault")
        self.items["Vault Key"] = Item(
            "Vault Key", None, used_in="Vault")  # revealed later

    # ---------- UI ----------

    def show_status(self):
        print("\n---")
        room = self.rooms[self.player.room]
        print(f"You are in the {room.name}.")
        print(room.desc)

        if room.clue:
            print("Clue:", room.clue)

        # Chamber dynamic description
        if room.name == "Chamber":
            ice_state = room.state.get("ice_state", "frozen")
            if ice_state == "frozen":
                print("The pool is frozen solid. Something glitters under the ice.")
            elif ice_state == "melted":
                print("The pool has melted. The water is too deep to cross.")
                if self.items["Vault Key"].location == "Chamber":
                    print("You see the Vault Key gleaming in the water.")
            elif ice_state == "refrozen":
                print(
                    "The pool has been refrozen into a bridge of ice. You can cross east to the Vault.")

        # Vault dynamic description & win check
        if room.name == "Vault":
            if room.state.get("open") == "true":
                print("The Gem of Eternity glows on the altar!")
                print(
                    "Congratulations! You have reached the Gem of Eternity and won the game!")
                raise SystemExit
            else:
                print("The vault door is shut. Perhaps a special stone could open it...")

        # Visible items
        visible = [it.name for it in self.items.values()
                   if it.location == room.name]
        for nm in visible:
            print(f"You see a {nm} here.")

        inv = ", ".join(self.player.inventory) or "empty"
        print("\nInventory:", inv)
        print("---")

    def show_help(self):
        print("""
Commands:
  go [direction]      - Move north, south, east, or west
  look                - Show room description and items
  pick [item]         - Pick up an item
  use [item]          - Use an item in the current room
  inventory, i        - Show your inventory
  help                - Show this help message
  quit, exit          - Quit the game
""")

    # ---------- Mechanics ----------

    def move(self, direction: str):
        room = self.rooms[self.player.room]
        if room.has_exit(direction):
            self.player.room = room.exits[direction]
            self.show_status()
        else:
            print("You can't go that way.")

    def pick(self, item_name: str):
        # Case-insensitive resolution
        lookup = {name.lower(): name for name in self.items}
        actual = lookup.get(item_name.lower())
        if not actual:
            print(f"There is no {item_name} here.")
            return

        item = self.items[actual]
        if item.location != self.player.room:
            print(f"There is no {actual} here.")
            return

        if self.player.has(actual):
            print(f"You already have the {actual}.")
            return

        self.player.add(actual)
        item.location = "inventory"
        print(f"You picked up the {actual}.")

    def use(self, item_name: str):
        # Case-insensitive resolution
        lookup = {name.lower(): name for name in self.items}
        actual = lookup.get(item_name.lower())
        if not actual or not self.player.has(actual):
            print(f"You don't have a {item_name}.")
            return

        room = self.rooms[self.player.room]
        # --- Room-specific effects ---
        if room.name == "Library" and actual == "Crystal Orb":
            if not room.has_exit("east"):
                print(
                    "You place the Crystal Orb on the pedestal. A hidden door opens to the east!")
                room.connect("east", "Altar")
                # Ensure back-link exists (already there): Altar->west
            else:
                print("The hidden door is already open.")

        elif room.name == "Altar" and actual == "Enchanted Rope":
            if not room.has_exit("north"):
                print(
                    "You lay the rope across the chasm below. The path north is now safe.")
                room.connect("north", "Chamber")
                # Chamber already has south->Altar
            else:
                print("The rope bridge is already in place.")

        elif room.name == "Chamber":
            ice_state = room.state.get("ice_state", "frozen")

            if actual == "Fire Scroll":
                if ice_state == "frozen":
                    print("You read the Fire Scroll. Flames dance across the pool, melting the ice! "
                          "The Vault Key gleams at the bottom.")
                    room.state["ice_state"] = "melted"
                    # Reveal the Vault Key here
                    key = self.items["Vault Key"]
                    if key.location is None:
                        key.location = "Chamber"
                else:
                    print("The fire crackles, but the pool is already melted.")

            elif actual == "Ice Wand":
                if ice_state == "melted":
                    print("You wave the Ice Wand. Frost races across the pool, freezing it solid again. "
                          "You can now cross to the east.")
                    room.state["ice_state"] = "refrozen"
                    # Unlock Chamber → Vault
                    if not room.has_exit("east"):
                        room.connect("east", "Vault")
                elif ice_state == "frozen":
                    print("The pool is already frozen solid.")
                elif ice_state == "refrozen":
                    print("The pool remains safe to cross.")

            else:
                print("Nothing happens.")

        elif room.name == "Vault" and actual == "Teleportation Stone":
            if self.player.has("Vault Key"):
                if room.state.get("open") != "true":
                    print("You activate the stone. The vault door swings open!")
                    room.state["open"] = "true"
                    # Safety: ensure Chamber knows the route (may already be set)
                    if not self.rooms["Chamber"].has_exit("east"):
                        self.rooms["Chamber"].connect("east", "Vault")
                    self.show_status()
                else:
                    print("The vault is already open.")
            else:
                print("The stone does nothing without a key.")

        else:
            print(f"You can't use {actual} here.")

    # ---------- Parser / Commands ----------

    def handle_go(self, args: List[str]):
        if not args:
            print("Go where? Try: go north")
            return
        d = self.DIR_ALIASES.get(args[0])
        if not d:
            print("I don’t recognize that direction. Try north/south/east/west.")
            return
        self.move(d)

    def handle_pick(self, args: List[str]):
        if not args:
            print("Pick what? Example: pick crystal orb")
            return
        name = " ".join(args).title()
        self.pick(name)

    def handle_use(self, args: List[str]):
        if not args:
            print("Use what? Example: use enchanted rope")
            return
        name = " ".join(args).title()
        self.use(name)

    def handle_look(self, args: List[str]):
        self.show_status()

    def handle_inventory(self, args: List[str]):
        inv = ", ".join(self.player.inventory) or "empty"
        print("Inventory:", inv)

    def handle_help(self, args: List[str]):
        self.show_help()

    def handle_quit(self, args: List[str]):
        print("Farewell, wizard!")
        raise SystemExit

    def process_command(self, cmd: str):
        text = cmd.strip().lower()
        if not text:
            return
        parts = text.split()
        raw_verb, args = parts[0], parts[1:]
        verb = self.VERB_ALIASES.get(raw_verb)
        if not verb:
            try:
                import difflib
                sug = difflib.get_close_matches(
                    raw_verb, self.VERB_ALIASES.keys(), n=1)
                if sug:
                    print(
                        f"Unknown command '{raw_verb}'. Did you mean '{sug[0]}'? (Type 'help' for commands.)")
                else:
                    print(
                        f"Unknown command '{raw_verb}'. Type 'help' for commands.")
            except Exception:
                print(
                    f"Unknown command '{raw_verb}'. Type 'help' for commands.")
            return

        handler = self.COMMANDS.get(verb)
        if handler:
            handler(args)
        else:
            print("That command exists but isn’t wired up yet. (Bug!)")

    # ---------- Run loop ----------

    def run(self):
        print("=== Wizard's Quest (OOP Edition) ===")
        self.show_status()
        while True:
            try:
                cmd = input("\n> ")
                self.process_command(cmd)
            except (EOFError, KeyboardInterrupt):
                print("\nFarewell, wizard!")
                break
            except SystemExit:
                break


# ----------------------------
# Entrypoint
# ----------------------------
if __name__ == "__main__":
    Game().run()
