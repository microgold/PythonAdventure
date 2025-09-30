import json
import html as ihtml
import streamlit as st
import streamlit.components.v1 as components
from OOAdventure.Game import Game


# ----------------------------
# Utilities
# ----------------------------

def append_output(line: str):
    st.session_state.transcript.append(line)

# ----------------------------
# Game state management (persist to/from JSON file)
# ----------------------------


def save_state(game: Game):
    with open("autosave.json", "w") as f:
        json.dump(game.to_dict(), f)


def load_state() -> Game:
    try:
        with open("autosave.json") as f:
            state = json.load(f)
        return Game.from_dict(state)   # restored instance
    except FileNotFoundError:
        return Game()


# ----------------------------
# Command processing
# Processes the command and captures output
# ----------------------------


def run_and_capture(game, cmd: str) -> str:
    """Capture command output from the game."""
    import io
    import sys
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        game.process_command(cmd)
    except SystemExit:
        print("Game Over. Refresh or restart to play again.")
    finally:
        sys.stdout = old
    return buf.getvalue()


# ----------------------------
# Page + Session state init
# ----------------------------
st.set_page_config("Wizard's Quest", layout="wide")

if "game" not in st.session_state:
    st.session_state.game = load_state()
    st.session_state.transcript = []
    append_output("=== Wizard's Quest ===")
    append_output(run_and_capture(st.session_state.game, "look"))

    # --- Save/Load controls ---
if "game" in st.session_state:
    st.markdown("### Save / Load")


# ----------------------------
# Layout
# Adds 2 columns: left=transcript, right=command + controls
# ----------------------------
col1, col2 = st.columns([3, 1])

# ==== Transcript (left) ====
#  monospace, dark background, auto-scroll to bottom
# - transcript is a list of adventures lines
# - only show last 400 lines (to avoid huge HTML)
# Auto-scroll to bottom via JS trick
with col1:
    st.markdown("### Transcript")
    transcript_text = "\n".join(st.session_state.transcript[-400:])
    transcript_html = f"""
    <div id="box" style="
        height: 500px;
        overflow-y: auto;
        background: #111;
        color: #eee;
        padding: 10px;
        font-family: monospace;
        white-space: pre-wrap;
        border-radius: 6px;">
      {ihtml.escape(transcript_text)}
    </div>
    <script>
      // After paint, scroll to bottom so latest output is visible
      setTimeout(function() {{
        var box = document.getElementById('box');
        if (box) box.scrollTop = box.scrollHeight;
      }}, 0);
    </script>
    """
    components.html(transcript_html, height=520, scrolling=False)

# ==== Command + controls (right) ====
# single-line text input, auto-focus
# this is where you enter commands

with col2:
    st.markdown("### Command")
    with st.form("command_form", clear_on_submit=True):
        cmd = st.text_input("Command", key="command_box",
                            placeholder="e.g., go east")
        submitted = st.form_submit_button("Send")
        if submitted and cmd.strip():
            out = run_and_capture(st.session_state.game, cmd)
            append_output(f"> {cmd}")
            append_output(out)
            save_state(st.session_state.game)
            st.rerun()

    st.markdown("")

    # --- Save/Load controls inside a "box" ---
    with st.container():
        st.markdown("### Save / Load")

        # Download current state
        save_bytes = json.dumps(
            st.session_state.game.to_dict(), indent=2).encode("utf-8")
        st.download_button(
            "Download Save",
            data=save_bytes,
            file_name="game_state.json",
            mime="application/json",
            use_container_width=True,
        )

        # Upload to restore state
        uploaded_file = st.file_uploader("Upload Save", type="json")
        if uploaded_file is not None:
            state = json.load(uploaded_file)
            st.session_state.game = Game.from_dict(state)
            st.session_state.transcript = []
            append_output("=== Restored Game ===")
            append_output(run_and_capture(st.session_state.game, "look"))
            save_state(st.session_state.game)
            st.rerun()

    # SINGLE robust focus script (post-render, via components.html)
    # works with keyed widget, label, placeholder, or auto id
    # tries to focus once immediately in the input box, else it sets a mutation observer
    # the mutation observer auto-stops after 5s (safety)
    # and also puts cursor at end of the input

    components.html(
        """
        <script>
          (function () {
            const P = window.parent && window.parent.document ? window.parent.document : document;

            function findInput() {
              const selectors = [
                'div[data-testid="stTextInput-command_box"] input[data-baseweb="input"]', // keyed widget
                'input[aria-label="Command"]',                                           // label
                'input[placeholder="e.g., go east"]',                                    // placeholder
                'input[id^="text_input"][type="text"]'                                   // Streamlit auto id
              ];
              for (const s of selectors) {
                const el = P.querySelector(s);
                if (el) return el;
              }
              return null;
            }

            function focusOnce() {
              const el = findInput();
              if (!el) return false;
              try {
                el.click();
                el.focus({ preventScroll: true });
                if (typeof el.setSelectionRange === 'function') {
                  const len = el.value.length;
                  el.setSelectionRange(len, len);
                }
              } catch (e) {}
              return true;
            }

            if (focusOnce()) return;

            const obs = new MutationObserver(() => {
              if (focusOnce()) obs.disconnect();
            });
            obs.observe(P.body, { childList: true, subtree: true });
            setTimeout(() => obs.disconnect(), 5000); // safety stop
          })();
        </script>
        """,
        height=0,
    )

    st.divider()
    if st.button("Restart (fresh game)", use_container_width=True):
        import os
        if os.path.exists("autosave.json"):
            os.remove("autosave.json")
        st.session_state.clear()
        st.rerun()
st.divider()
