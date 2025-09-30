from . import UseStrategyBase


class VaultUse(UseStrategyBase):
    def use(self, game: "Game", item_name: str) -> None:
        room = game.room("Vault")
        if item_name == "Teleportation Stone":
            if game.player.has("Vault Key"):
                if not room.state.get("open"):
                    print("You activate the stone. The vault door swings open!")
                    room.state["open"] = True
                    # Safety: ensure Chamber → Vault is present
                    if not game.room("Chamber").has_exit("east"):
                        game.room("Chamber").connect("east", "Vault")
                    game.show_status()  # will end the game here
                else:
                    print("The vault is already open.")
            else:
                print("The stone does nothing without a key.")
        else:
            print("Nothing happens.")
