#!/usr/bin/env python3
import io
import json
import tempfile
from typing import List, Tuple

import gradio as gr
from OOAdventure.Game import Game  # your OO engine


# ----------------------------
# Helpers
# ----------------------------

def run_and_capture(game: Game, cmd: str) -> str:
    """Run a command and capture printed output."""
    import sys
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        game.process_command(cmd)
    except SystemExit:
        # Keep the app alive; just show a celebratory message.
        print("🎉 Congratulations! You completed the quest!")
    finally:
        sys.stdout = old
    return buf.getvalue().strip()


def bootstrap() -> Tuple[List[Tuple[str, str]], Game]:
    """New game + initial 'look' as a bot message."""
    g = Game()
    first = run_and_capture(g, "look")
    # Chatbot expects pairs: (user, bot). For the first screen, bot-only is fine with empty user.
    chat = [("", f"=== Wizard's Quest — Gradio Edition ===\n{first}")]
    return chat, g


def on_send(cmd: str, chat: List[Tuple[str, str]], game: Game):
    """Handle a command: append (user, bot) pair."""
    if game is None:
        chat, game = bootstrap()

    cmd = (cmd or "").strip()
    if not cmd:
        return chat, game, ""  # just clear the box

    out = run_and_capture(game, cmd)
    chat = chat + [(f"> {cmd}", out or "(no output)")]
    return chat, game, ""  # clear input


def on_restart():
    """Start fresh."""
    return bootstrap()


# ------- Save / Load (legacy-compatible) -------

def on_download_legacy(chat: List[Tuple[str, str]], game: Game):
    """
    Create a temp JSON save file for older Gradio versions.
    Returns a file path that a File component can serve for download.
    """
    if game is None:
        chat, game = bootstrap()
    payload = {
        "game": game.to_dict(),
        "chat": chat,
    }
    data = json.dumps(payload, indent=2).encode("utf-8")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    tmp.write(data)
    tmp.flush()
    tmp.close()
    return tmp.name


def on_upload_legacy(upload):
    """
    Load save from a JSON file uploaded via gr.File.
    Supports both 'chat' style and older 'transcript' text.
    """
    if upload is None:
        return gr.update(), gr.update()

    try:
        with open(upload.name, "rb") as f:
            raw = f.read().decode("utf-8")
        state = json.loads(raw)

        # Rebuild game
        game = Game.from_dict(state["game"])

        # Rebuild chat
        if "chat" in state and isinstance(state["chat"], list):
            chat = state["chat"]
        else:
            # Back-compat: convert a text transcript to simple pairs
            transcript = state.get("transcript", "")
            blocks = [b for b in transcript.split("\n\n") if b.strip()]
            chat = []
            for b in blocks:
                # best-effort: put block in bot bubble
                chat.append(("", b))

        # Add a fresh LOOK to anchor the UI
        look = run_and_capture(game, "look")
        chat = chat + [("", f"(Resumed) {look}")]
        return chat, game

    except Exception as e:
        return [("", f"Error loading save: {e}")], None


# ----------------------------
# UI
# ----------------------------

with gr.Blocks(title="Wizard's Quest", css="footer {display:none !important;}") as demo:
    gr.Markdown("# 🧙 Wizard's Quest — Gradio Edition")
    gr.Markdown(
        "Type commands like **go north**, **pick orb**, **use stone**, **look**, **help**.  \n"
        "Use **Download Save**/**Upload Save** to persist progress."
    )

    # Per-user state
    chat_state = gr.State()   # List[Tuple[str,str]]
    game_state = gr.State()   # Game

    with gr.Row():
        with gr.Column(scale=3):
            chat = gr.Chatbot(label="Transcript", height=560,
                              show_copy_button=True)
        with gr.Column(scale=1):
            cmd = gr.Textbox(
                label="Command", placeholder="e.g., go east", autofocus=True)
            send = gr.Button("Send", variant="primary")

            restart = gr.Button("🔄 Restart (fresh game)")

            gr.Markdown("### Save / Load")
            download_btn = gr.Button("💾 Download Save")
            download_file = gr.File(label="Your save file", interactive=False)
            upload_file = gr.File(
                label="Upload Save (.json)", file_types=[".json"])

    # Initialize state on app load
    def _load():
        c, g = bootstrap()
        return c, g, c

    demo.load(_load, inputs=None, outputs=[chat_state, game_state, chat])

    # Send command (button)
    send.click(
        on_send,
        inputs=[cmd, chat_state, game_state],
        outputs=[chat_state, game_state, cmd],
    ).then(
        lambda c: c,  # reflect latest chat_state in UI
        inputs=[chat_state],
        outputs=[chat],
    )

    # Send command (press Enter)
    cmd.submit(
        on_send,
        inputs=[cmd, chat_state, game_state],
        outputs=[chat_state, game_state, cmd],
    ).then(
        lambda c: c,
        inputs=[chat_state],
        outputs=[chat],
    )

    # Restart
    restart.click(
        lambda: on_restart(),
        inputs=None,
        outputs=[chat_state, game_state],
    ).then(
        lambda c: c,
        inputs=[chat_state],
        outputs=[chat],
    )

    # Download save (legacy-compatible path via File)
    download_btn.click(
        on_download_legacy,
        inputs=[chat_state, game_state],
        outputs=[download_file],
    )

    # Upload save
    upload_file.change(
        on_upload_legacy,
        inputs=[upload_file],
        outputs=[chat_state, game_state],
    ).then(
        lambda c: c,
        inputs=[chat_state],
        outputs=[chat],
    )


if __name__ == "__main__":
    demo.launch()
