
# 🧙 Wizard’s Quest — Python Adventure Game

Welcome to **Wizard’s Quest**, a text-based adventure game written in Python and powered by **Gradio** for a modern, browser-friendly interface.

This project is part of the *Python Adventures* book — walking you step by step from the basics of Python into building and deploying your own adventure games.

Play it directly in your browser, or run it locally to hack on the code and create your own quests.

---

## 🚀 Live Demo

👉 [Play on Hugging Face](https://huggingface.co/spaces/microgold/PythonAdventures)

---

## 📦 Installation (Local)

1. Clone the repo:

   ```bash
   git clone https://huggingface.co/spaces/microgold/PythonAdventures
   cd PythonAdventures
   ```

2. Create a virtual environment (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate   # Mac/Linux
   venv\Scripts\activate      # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the app:

   ```bash
   python app.py
   ```

5. Open [http://localhost:7860](http://localhost:7860) in your browser.

---

## 🗂 Project Structure

```
PythonAdventures/
│── app.py            # Gradio wrapper (entrypoint for Hugging Face)
│── OOAdventure/      # Core game engine (OO design with Items, Rooms, etc.)
│── requirements.txt
│── README.md
```

---

## 📝 Features

* Fully text-based **adventure engine** in Python
* Object-oriented design (Rooms, Items, Player, Strategies)
* Save/Load your game state as JSON
* Web interface via **Gradio**
* Deployable free on Hugging Face

---

## ❓ FAQ / Gotchas

**Q: Why do I get `ImportError: attempted relative import with no known parent package` when running locally?**
A: You’re probably running a file directly. Use the `-m` flag so Python treats the folder as a package:

```bash
python -m OOAdventure.test
```

**Q: My input box doesn’t get focus when I reload the page.**
A: On Streamlit this was tricky, but in Gradio it’s solved by using `Chatbot(type="messages")`. If you cloned older code, make sure you’re on the Gradio edition.

**Q: After cloning your repo, I can’t push changes back.**
A: That’s expected — you don’t have write access to my Space. You need to either:

* **Option C:** Clone my repo, then point the Git remote to your own Hugging Face Space:

  ```bash
  git remote set-url origin https://huggingface.co/spaces/<your-username>/<your-space>
  ```
* **Option D:** Fork (duplicate) the Space from the Hugging Face UI. That’s the easiest way if you don’t want to touch Git config.

**Q: Do I need to flatten the OOAdventure package into the root to make Hugging Face work?**
A: No. Just add an empty `__init__.py` inside `OOAdventure/` and use relative imports (e.g. `from .Room import Room`).

**Q: Where is my game state saved?**
A: Locally it writes to `autosave.json`. On Hugging Face Spaces, this file will reset each time the container restarts. For persistent saves, use the **Download Save** / **Upload Save** buttons in the UI.

**Q: Can I make my own rooms, items, or puzzles?**
A: Absolutely! Add new classes or extend existing ones in `OOAdventure/`. The Strategy pattern makes it easy to define custom room logic.

---

## 🧭 Next Steps

* Add your own items and puzzles.
* Customize room descriptions.
* Fork this repo and create a new Hugging Face Space under your account.
* Share your game with the world!

---

Would you like me to also add a **“Troubleshooting Hugging Face Deployment”** section (build errors, missing requirements, etc.) to the FAQ, since that’s another common stumbling block?



---
title: PythonAdventures
emoji: 🏆
colorFrom: gray
colorTo: pink
sdk: gradio
sdk_version: 5.47.2
app_file: app.py
pinned: false
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference
