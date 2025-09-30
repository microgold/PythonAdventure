from . import UseStrategyBase


class ChamberUse(UseStrategyBase):
    def use(self, game: "Game", item_name: str) -> None:
        room = game.room("Chamber")
        ice = room.state.get("ice_state", "frozen")

        if item_name == "Fire Scroll":
            if ice == "frozen":
                print("You read the Fire Scroll. Flames dance across the pool, melting the ice! "
                      "The Vault Key gleams at the bottom.")
                room.state["ice_state"] = "melted"
                key = game.items["Vault Key"]
                if key.location is None:
                    key.location = "Chamber"
            else:
                print("The fire crackles, but the pool is already melted.")

        elif item_name == "Ice Wand":
            if ice == "melted":
                print("You wave the Ice Wand. Frost races across the pool, freezing it solid again. "
                      "You can now cross to the east.")
                room.state["ice_state"] = "refrozen"
                if not room.has_exit("east"):
                    room.connect("east", "Vault")
            elif ice == "frozen":
                print("The pool is already frozen solid.")
            elif ice == "refrozen":
                print("The pool remains safe to cross.")
        else:
            print("Nothing happens.")
