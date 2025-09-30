from . import PickStrategyBase


class ChamberPick(PickStrategyBase):
    def on_pick(self, game: "Game", item_name: str) -> None:
        if item_name == "Vault Key":
            print("The key is cold to the touch.")
