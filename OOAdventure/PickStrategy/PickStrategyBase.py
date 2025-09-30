class PickStrategyBase:
    def on_pick(self, game: "Game", item_name: str) -> None:
        # Optional hook per-room after a successful pick
        pass
