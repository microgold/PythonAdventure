import io
import sys
import pytest
from OOAdventure.Game import Game  # your OO game


def run_command(game, cmd: str) -> str:
    """Capture printed output from a game command."""
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        game.process_command(cmd)
    except SystemExit:
        pass  # Game may call exit() when you win
    finally:
        sys.stdout = old
    return buf.getvalue()


def test_full_walkthrough():
    game = Game()
    transcript = []

    # Play the game through
    transcript.append(run_command(game, "look"))
    transcript.append(run_command(game, "pick stone"))
    transcript.append(run_command(game, "go north"))
    transcript.append(run_command(game, "pick orb"))
    transcript.append(run_command(game, "use orb"))
    transcript.append(run_command(game, "go east"))
    transcript.append(run_command(game, "pick rope"))
    transcript.append(run_command(game, "use rope"))
    transcript.append(run_command(game, "go north"))
    transcript.append(run_command(game, "pick fire"))
    transcript.append(run_command(game, "pick wand"))
    transcript.append(run_command(game, "use fire scroll"))
    transcript.append(run_command(game, "pick key"))
    transcript.append(run_command(game, "use wand"))
    transcript.append(run_command(game, "go east"))
    transcript.append(run_command(game, "use stone"))

    joined = "\n".join(transcript)

    # Key checkpoints
    assert "You picked up the Teleportation Stone." in joined
    assert "The vault door swings open!" in joined
    assert "Congratulations! You have reached the Gem of Eternity" in joined
