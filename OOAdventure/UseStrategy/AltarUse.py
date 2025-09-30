from . import UseStrategyBase


class AltarUse(UseStrategyBase):
    def use(self, game: "Game", item_name: str) -> None:
        if item_name == "Enchanted Rope":
            room = game.room("Altar")
            if not room.has_exit("north"):
                print(
                    "You lay the rope across the chasm below. The path north is now safe.")
                room.connect("north", "Chamber")
            else:
                print("The rope bridge is already in place.")
        else:
            print("Nothing happens.")
