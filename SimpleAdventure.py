#!/usr/bin/env python3
"""
A very short adventure game.
The player is a wizard who explores rooms, collects items,
and must use them in the right order to reach the treasure.

Walkthrough:
- Start at Entrance. Pick up the Teleportation Stone.
- Go north to Library. Pick up the Crystal Orb.
- Use Crystal Orb in Library to unlock east exit.
- Go east to Altar. Pick up Enchanted Rope.
- Use Enchanted Rope in Altar to unlock north exit.
- Go north to Chamber. Pick up Fire Scroll and Ice Wand.
- Use Fire Scroll or Ice Wand in Chamber to get Vault Key.
- Go east to Vault.
- Use Teleportation Stone in Vault (must have Vault Key) to open the vault.
- Win by reaching the Gem of Eternity!
"""

# ---------- Items ----------
items = {
    "Crystal Orb": {
        "location": "Library",
        "used_in": "Library",
        "aliases": ["orb"]
    },
    "Enchanted Rope": {
        "location": "Altar",
        "used_in": "Chasm",
        "aliases": ["rope"]
    },
    "Fire Scroll": {
        "location": "Chamber",
        "used_in": "Ice Pool",
        "aliases": ["fire", "scroll"]
    },
    "Ice Wand": {
        "location": "Chamber",
        "used_in": "Ice Pool",
        "aliases": ["ice", "wand"]
    },
    "Teleportation Stone": {
        "location": "Entrance",
        "used_in": "Vault",
        "aliases": ["stone", "teleporter", "tp stone"]
    },
    "Vault Key": {
        "location": None,
        "used_in": "Vault",
        "aliases": ["key"]
    }
}

# ---------- UI ----------


def resolve_item_name(raw_name):
    key = raw_name.lower()
    for name, data in items.items():
        # Check full name
        if key == name.lower():
            return name
        # Check aliases
        if "aliases" in data:
            for alias in data["aliases"]:
                if key == alias.lower():
                    return name
    return None


def show_status():
    print("\n---")
    print(f"You are in the {player['room']}.")
    print(rooms[player["room"]]["desc"])
    clue = rooms[player["room"]].get("clue")
    if clue:
        print("Clue:", clue)
    if player["room"] == "Chamber":
        print("There is a pool of ice and a flame here.")
    elif player["room"] == "Vault":
        print("The Gem of Eternity glows on the altar!")
        if rooms["Vault"].get("open", False):
            print(
                "Congratulations! You have reached the Gem of Eternity and won the game!")
            exit()
        else:
            print("The vault door is shut. Perhaps a special stone could open it...")
    for name, data in items.items():
        if data["location"] == player["room"]:
            print(f"You see a {name} here.")
    print("\nInventory:", ", ".join(player["inventory"]) or "empty")
    print("---")


def show_help():
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


def move(direction):
    current = rooms[player["room"]]
    if direction in current:
        next_room = current[direction]
        # FIX: allow entering Vault even if not open,
        # so you can use the Teleportation Stone inside.
        player["room"] = next_room
        show_status()
    else:
        print("You can't go that way.")


def use(item_name):
    if item_name not in player["inventory"]:
        print(f"You don't have a {item_name}.")
        return

    room = player["room"]
    if room == "Library" and item_name == "Crystal Orb":
        if "east" not in rooms["Library"]:
            print(
                "You place the Crystal Orb on the pedestal. A hidden door opens to the east!")
            rooms["Library"]["east"] = "Altar"
        else:
            print("The hidden door is already open.")
    elif room == "Altar" and item_name == "Enchanted Rope":
        if "north" not in rooms["Altar"]:
            print("You lay the rope across the chasm below. The path north is now safe.")
            rooms["Altar"]["north"] = "Chamber"
        else:
            print("The rope bridge is already in place.")
    elif room == "Chamber":
        state = rooms["Chamber"]["ice_state"]

        if item_name == "Fire Scroll":
            if state == "frozen":
                print("You read the Fire Scroll. Flames dance across the pool, melting the ice! "
                      "The Vault Key gleams at the bottom.")
                rooms["Chamber"]["ice_state"] = "melted"
                # place the key here
                items["Vault Key"]["location"] = "Chamber"
            else:
                print("The fire crackles, but the pool is already melted.")

        elif item_name == "Ice Wand":
            if state == "melted":
                print("You wave the Ice Wand. Frost races across the pool, freezing it solid again. "
                      "You can now cross to the east.")
                rooms["Chamber"]["ice_state"] = "refrozen"
                rooms["Chamber"]["east"] = "Vault"  # unlock Vault path
            elif state == "frozen":
                print("The pool is already frozen solid.")
            elif state == "refrozen":
                print("The pool remains safe to cross.")
        else:
            print("Nothing happens.")
    elif room == "Vault" and item_name == "Teleportation Stone":
        if "Vault Key" in player["inventory"]:
            if not rooms["Vault"].get("open", False):
                print("You activate the stone. The vault door swings open!")
                rooms["Vault"]["open"] = True
                # (Optional) ensure the path from Chamber is known; keep as-is
                rooms["Chamber"]["east"] = "Vault"
                show_status()
            else:
                print("The vault is already open.")
        else:
            print("The stone does nothing without a key.")
    else:
        print(f"You can't use {item_name} here.")


def pick(item_name):
    if not item_name:
        print(f"There is no {item_name} here.")
        return
    data = items[item_name]
    if data["location"] != player["room"]:
        print(f"There is no {item_name} here.")
        return
    if item_name in player["inventory"]:
        print(f"You already have the {item_name}.")
        return
    player["inventory"].append(item_name)
    data["location"] = "inventory"
    print(f"You picked up the {item_name}.")


DIR_ALIASES = {
    "n": "north", "s": "south", "e": "east", "w": "west",
    "north": "north", "south": "south", "east": "east", "west": "west"
}


def handle_go(args):
    if not args:
        print("Go where? Try: go north")
        return
    direction = DIR_ALIASES.get(args[0])
    if not direction:
        print("I don’t recognize that direction. Try north/south/east/west.")
        return
    move(direction)


def handle_pick(args):
    if not args:
        print("Pick what? Example: pick crystal orb")
        return
    raw_item_name = " ".join(args).title()
    item_name = resolve_item_name(raw_item_name)
    if item_name:
        pick(item_name)
    else:
        print(f"There is no {raw_item_name} here.")


def handle_use(args):
    if not args:
        print("Use what? Example: use enchanted rope")
        return
    item_name = " ".join(args).title()
    raw_item_name = " ".join(args).title()
    item_name = resolve_item_name(raw_item_name)
    if item_name:
        use(item_name)
    else:
        print(f"There is no {raw_item_name} here.")


def handle_look(args):
    show_status()


def handle_inventory(args):
    print("Inventory:", ", ".join(player["inventory"]) or "empty")


def handle_help(args):
    show_help()


def handle_quit(args):
    print("Farewell, wizard!")
    exit()


COMMANDS = {
    "go": handle_go,
    "pick": handle_pick,
    "use": handle_use,
    "look": handle_look,
    "inventory": handle_inventory,
    "help": handle_help,
    "quit": handle_quit
}

VERB_ALIASES = {
    "go": "go", "move": "go", "walk": "go",
    "pick": "pick", "take": "pick", "get": "pick", "grab": "pick",
    "use": "use",
    "look": "look", "l": "look", "examine": "look",
    "inventory": "inventory", "i": "inventory",
    "help": "help", "quit": "quit", "exit": "quit"
}


def process_command(cmd):
    text = cmd.strip().lower()
    if not text:
        return

    parts = text.split()
    raw_verb = parts[0]
    args = parts[1:]

    verb = VERB_ALIASES.get(raw_verb)
    if not verb:
        # Optional nicety: a tiny suggestion if they’re close
        try:
            import difflib
            suggestion = difflib.get_close_matches(
                raw_verb, VERB_ALIASES.keys(), n=1)
            if suggestion:
                print(
                    f"Unknown command '{raw_verb}'. Did you mean '{suggestion[0]}'? (Type 'help' for commands.)")
            else:
                print(
                    f"Unknown command '{raw_verb}'. Type 'help' for commands.")
        except Exception:
            print(f"Unknown command '{raw_verb}'. Type 'help' for commands.")
        return

    handler = COMMANDS.get(verb)
    if handler:
        handler(args)
    else:
        print("That command exists but isn’t wired up yet. (Bug!)")


# ---------- World ----------
rooms = {
    "Entrance": {
        "north": "Library",
        "desc": "You stand at the grand entrance of the ancient tower."
    },
    "Library": {
        "south": "Entrance",
        # 'east' is locked until you use the Crystal Orb
        "desc": "Dusty books line the walls. A faint glow comes from a pedestal.",
        "clue": "A crystal orb must be placed on the pedestal to reveal the path east."
    },
    "Altar": {
        "west": "Library",
        # 'north' is locked until you use the Enchanted Rope
        "desc": "An altar with runes that pulse softly. A deep chasm blocks the northern path.",
        "clue": "You need an enchanted rope to cross the chasm below."
    },
    "Chamber": {
        "south": "Altar",
        # Note: "east" will be locked until the puzzle is solved
        "desc": "The chamber contains a frozen pool. Something glitters beneath the ice.",
        "clue": "Perhaps fire could melt the ice, and cold could make it safe again.",
        "ice_state": "frozen"  # frozen → melted → refroze
    },
    "Vault": {
        "west": "Chamber",
        "desc": "A vault door bars your way. The Gem of Eternity sits on a stone altar inside.",
        "clue": "You need the teleportation stone (and a key) to open this vault from here.",
        "open": False
    }
}

# ---------- State ----------
player = {"room": "Entrance", "inventory": []}

# ---------- Main ----------
print("=== Wizard's Quest ===")
show_status()

while True:
    cmd = input("\n> ")
    process_command(cmd)
