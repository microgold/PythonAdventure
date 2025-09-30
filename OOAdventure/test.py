from OOAdventure.Game import Game

if __name__ == "__main__":
    import os
    if os.path.exists("autosave.json"):
        choice = input(
            "Found a saved game. Do you want to load it? (y/n) ").strip().lower()
        if choice.startswith("y"):
            game = Game.load("autosave.json")
        else:
            game = Game()
    else:
        game = Game()

    game.run()
