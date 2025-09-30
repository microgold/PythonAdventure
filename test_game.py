import unittest
import io
import sys
from OOAdventure.Game import Game  # import your OO game


class TestGame(unittest.TestCase):

    def run_command(self, game, cmd: str) -> str:
        """Helper to capture printed output from a game command."""
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            game.process_command(cmd)
        except SystemExit:
            pass  # Game may call exit when you win
        finally:
            sys.stdout = old
        return buf.getvalue()

    def test_full_walkthrough(self):
        game = Game()
        transcript = []

        # Step 1: Look around
        transcript.append(self.run_command(game, "look"))
        # Step 2: Pick up the teleportation stone
        transcript.append(self.run_command(game, "pick stone"))
        # Step 3: Go north to library
        transcript.append(self.run_command(game, "go north"))
        transcript.append(self.run_command(game, "pick orb"))
        transcript.append(self.run_command(game, "use orb"))
        transcript.append(self.run_command(game, "go east"))
        transcript.append(self.run_command(game, "pick rope"))
        transcript.append(self.run_command(game, "use rope"))
        transcript.append(self.run_command(game, "go north"))
        transcript.append(self.run_command(game, "pick fire"))
        transcript.append(self.run_command(game, "pick wand"))
        transcript.append(self.run_command(game, "use fire scroll"))
        transcript.append(self.run_command(game, "pick key"))
        transcript.append(self.run_command(game, "use wand"))
        transcript.append(self.run_command(game, "go east"))
        transcript.append(self.run_command(game, "use stone"))

        joined = "\n".join(transcript)

        # Assert some important checkpoints
        self.assertIn("You picked up the Teleportation Stone.", joined)
        self.assertIn("The vault door swings open!", joined)
        self.assertIn(
            "Congratulations! You have reached the Gem of Eternity", joined)


if __name__ == "__main__":
    unittest.main()
