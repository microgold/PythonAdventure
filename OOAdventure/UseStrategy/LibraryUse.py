from . import UseStrategyBase


class LibraryUse(UseStrategyBase):
    def use(self, game: "Game", item_name: str) -> None:
        if item_name == "Crystal Orb":
            room = game.room("Library")
            if not room.has_exit("east"):
                print(
                    "You place the Crystal Orb on the pedestal. A hidden door opens to the east!")
                room.connect("east", "Altar")
            else:
                print("The hidden door is already open.")
        else:
            print("Nothing happens.")
