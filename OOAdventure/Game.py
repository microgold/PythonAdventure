

import json
from pathlib import Path
from typing import Dict, List, Optional
from .Item import Item
from .PickStrategy import ChamberPick
from .Room import Room
from .Player import Player
from .UseStrategy import VaultUse
from .UseStrategy import AltarUse
from .UseStrategy import ChamberUse
from .UseStrategy import LibraryUse


class Game:
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.items: Dict[str, Item] = {}
        self.player = Player()

        # Directions & verbs
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
            "help": "help", "quit": "quit", "exit": "quit",
            "save": "save", "load": "load",
            "restart": "restart", "reset": "restart"
        }
        self.COMMANDS = {
            "go": self.handle_go,
            "pick": self.handle_pick,
            "use": self.handle_use,
            "look": self.handle_look,
            "inventory": self.handle_inventory,
            "help": self.handle_help,
            "quit": self.handle_quit,
            "save": self.handle_save,
            "load": self.handle_load,
            "restart": self.handle_restart
        }

        self._build_world()
        self._build_item_alias_index()

    # ----- helpers -----
    def room(self, name: str) -> Room:
        return self.rooms[name]

    def _normalize(self, s: str) -> str:
        return s.strip().lower().strip('"').strip("'")

    def _build_item_alias_index(self) -> None:
        self.item_alias_index: Dict[str, str] = {}
        for canon, it in self.items.items():
            self.item_alias_index[self._normalize(canon)] = canon
            for a in it.aliases:
                self.item_alias_index[self._normalize(a)] = canon

    def resolve_item_name(self, raw: str) -> Optional[str]:
        if not raw:
            return None
        key = self._normalize(raw)
        return self.item_alias_index.get(key)

    # ----- world setup -----
    def _build_world(self) -> None:
        # Rooms
        self.rooms["Entrance"] = Room(
            name="Entrance",
            desc="You stand at the grand entrance of the ancient tower."
        )
        self.rooms["Library"] = Room(
            name="Library",
            desc="Dusty books line the walls. A faint glow comes from a pedestal.",
            clue="A crystal orb must be placed on the pedestal to reveal the path east.",
            use_strategy=LibraryUse()
        )
        self.rooms["Altar"] = Room(
            name="Altar",
            desc="An altar with runes that pulse softly. A deep chasm blocks the northern path.",
            clue="You need an enchanted rope to cross the chasm below.",
            use_strategy=AltarUse()
        )
        self.rooms["Chamber"] = Room(
            name="Chamber",
            desc="The chamber contains a frozen pool. Something glitters beneath the ice.",
            clue="Perhaps fire could melt the ice, and cold could make it safe again.",
            state={"ice_state": "frozen"},
            use_strategy=ChamberUse(),
            pick_strategy=ChamberPick()
        )
        self.rooms["Vault"] = Room(
            name="Vault",
            desc="A vault door bars your way. The Gem of Eternity sits on a stone altar inside.",
            clue="You need the teleportation stone (and a key) to open this vault from here.",
            state={"open": False},
            use_strategy=VaultUse()
        )

        # Exits (gated exits are omitted until unlocked)
        self.room("Entrance").connect("north", "Library")
        self.room("Library").connect("south", "Entrance")
        self.room("Altar").connect("west", "Library")
        self.room("Chamber").connect("south", "Altar")
        self.room("Vault").connect("west", "Chamber")

        # Items (+ aliases)
        self.items["Crystal Orb"] = Item(
            "Crystal Orb", "Library", used_in="Library", aliases=["orb"])
        self.items["Enchanted Rope"] = Item(
            "Enchanted Rope", "Altar", used_in="Chasm", aliases=["rope"])
        self.items["Fire Scroll"] = Item(
            "Fire Scroll", "Chamber", used_in="Ice Pool", aliases=["fire", "scroll"])
        self.items["Ice Wand"] = Item(
            "Ice Wand", "Chamber", used_in="Ice Pool", aliases=["ice", "wand"])
        self.items["Teleportation Stone"] = Item("Teleportation Stone", "Entrance", used_in="Vault",
                                                 aliases=["stone", "teleporter", "tp stone"])
        self.items["Vault Key"] = Item(
            "Vault Key", None, used_in="Vault", aliases=["key"])

    # ----- UI / status -----
    def show_status(self) -> None:
        print("\n---")
        room = self.room(self.player.room)
        print(f"You are in the {room.name}.")
        print(room.desc)
        if room.clue:
            print("Clue:", room.clue)

        # Dynamic descriptions
        if room.name == "Chamber":
            ice = room.state.get("ice_state", "frozen")
            if ice == "frozen":
                print("The pool is frozen solid. Something glitters under the ice.")
            elif ice == "melted":
                print("The pool has melted. The water is too deep to cross.")
                if self.items["Vault Key"].location == "Chamber":
                    print("You see the Vault Key gleaming in the water.")
            elif ice == "refrozen":
                print(
                    "The pool has been refrozen into a bridge of ice. You can cross east to the Vault.")

        if room.name == "Vault":
            if room.state.get("open"):
                print("The Gem of Eternity glows on the altar!")
                print(
                    "Congratulations! You have reached the Gem of Eternity and won the game!")
                raise SystemExit
            else:
                print("The vault door is shut. Perhaps a special stone could open it...")

        # Visible items
        for it in self.items.values():
            if it.location == room.name:
                print(f"You see a {it.name} here.")

        inv = ", ".join(self.player.inventory) or "empty"
        print("\nInventory:", inv)
        print("---")

    def show_help(self) -> None:
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

    # ----- mechanics -----
    def move(self, direction: str) -> None:
        rm = self.room(self.player.room)
        if rm.has_exit(direction):
            self.player.room = rm.exits[direction]
            self.show_status()
        else:
            print("You can't go that way.")

    def pick(self, item_name: str) -> None:
        # canonical name assumed (resolver runs in parser)
        item = self.items.get(item_name)
        room = self.room(self.player.room)
        if not item or item.location != room.name:
            print(f"There is no {item_name} here.")
            return
        if self.player.has(item_name):
            print(f"You already have the {item_name}.")
            return
        self.player.add(item_name)
        item.location = "inventory"
        print(f"You picked up the {item_name}.")
        # Strategy hook
        if room.pick_strategy:
            room.pick_strategy.on_pick(self, item_name)

    def use(self, item_name: str) -> None:
        # canonical name assumed (resolver runs in parser)
        if not self.player.has(item_name):
            print(f"You don't have a {item_name}.")
            return
        room = self.room(self.player.room)
        if room.use_strategy:
            room.use_strategy.use(self, item_name)
        else:
            print("Nothing happens.")

    # ----- parser -----
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
            print("Pick what? Example: pick orb")
            return
        raw = " ".join(args)  # keep raw for aliases like "tp stone"
        canon = self.resolve_item_name(raw)
        if canon:
            self.pick(canon)
        else:
            print(f"There is no {raw} here.")

    def handle_use(self, args: List[str]):
        if not args:
            print("Use what? Example: use stone")
            return
        raw = " ".join(args)
        canon = self.resolve_item_name(raw)
        if canon:
            self.use(canon)
        else:
            print(f"You don't have a {raw}.")

    def handle_look(self, args: List[str]):
        self.show_status()

    def handle_inventory(self, args: List[str]):
        print("Inventory:", ", ".join(self.player.inventory) or "empty")

    def handle_help(self, args: List[str]):
        self.show_help()

    def handle_quit(self, args: List[str]):
        print("Saving game before exit...")
        try:
            self.save("autosave.json")
        except Exception as e:
            print(f"Warning: could not autosave: {e}")
        print("Farewell, wizard!")
        raise SystemExit

    def handle_save(self, args):
        path = args[0] if args else "save.json"
        try:
            self.save(path)
        except Exception:
            print("Could not save game.")

    def handle_load(self, args):
        path = args[0] if args else "save.json"
        try:
            new_game = Game.load(path)   # returns a new instance
            # Swap state into current loop
            self.rooms = new_game.rooms
            self.items = new_game.items
            self.player = new_game.player
            print("Loaded. Type 'look' to resume.")
        except Exception:
            print("Could not load game.")

    def handle_restart(self, args):
        import os
        if os.path.exists("autosave.json"):
            os.remove("autosave.json")
        print("Progress cleared. Restart the game to begin a new adventure.")
        raise SystemExit

    def to_dict(self) -> dict:
        # Player state
        player_data = {
            "room": self.player.room,
            "inventory": list(self.player.inventory)
        }

        # Items: only location needs to be saved (names are keys)
        items_data = {
            name: {"location": it.location}
            for name, it in self.items.items()
        }

        # Rooms: exits and state can change during play
        rooms_data = {
            name: {
                "exits": dict(rm.exits),
                "state": dict(rm.state)
            }
            for name, rm in self.rooms.items()
        }

        return {
            "version": 1,
            "player": player_data,
            "items": items_data,
            "rooms": rooms_data
        }

    def save(self, path: str = "save.json") -> None:
        data = self.to_dict()
        Path(path).write_text(json.dumps(data, indent=2))
        print(f"Game saved to {path}.")

    @classmethod
    def load(cls, path: str = "save.json") -> "Game":
        try:
            raw = Path(path).read_text()
            data = json.loads(raw)
        except FileNotFoundError:
            print(f"No save found at {path}.")
            raise
        except json.JSONDecodeError as e:
            print(f"Save file is corrupted or invalid JSON: {e}")
            raise

        game = cls.from_dict(data)
        print(f"Game loaded from {path}.")
        return game

    @classmethod
    def from_dict(cls, data: dict) -> "Game":
     # 1) Create a fresh game (builds rooms/items/strategies)
        game = cls()

      # 2) Optional: handle version differences gracefully
        version = data.get("version", 1)
        if version != 1:
            print(
                f"Warning: save version {version} not recognized by loader v1. Attempting best-effort load.")

            # 3) Restore player
        p = data["player"]
        game.player.room = p["room"]
        game.player.inventory = list(p.get("inventory", []))

        # 4) Restore items (locations)
        for name, item_data in data.get("items", {}).items():
            if name in game.items:
                game.items[name].location = item_data.get("location")

        # 5) Restore rooms (exits + state)
        for name, room_data in data.get("rooms", {}).items():
            if name in game.rooms:
                rm = game.rooms[name]
                rm.exits = dict(room_data.get("exits", rm.exits))
                rm.state = dict(room_data.get("state", rm.state))

        return game

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

    # ----- run loop -----
    def run(self):
        print("=== Wizard's Quest (OOP + Strategy) ===")
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
