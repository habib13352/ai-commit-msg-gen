# AI Commit Message Generator

A minimal CLI utility that reads your staged Git diff and uses OpenAI’s API to suggest descriptive commit messages.

---

## 📋 Prerequisites

1. **Git** installed (so `git diff --cached` and `git commit` work).
2. **Python 3.8+** installed.
3. An **OpenAI API Key**.

---

## 🛠️ Setup

1. **Clone or download** this repo to your local machine.
2. **Install dependencies globally** (or into whichever Python environment you use):
   ```bash
   pip install openai python-dotenv
   ```
3. **Copy `.env.example` to `.env`** and insert your real API key:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` so that it reads:
   ```
   OPENAI_API_KEY=sk-...
   ```
4. **Ensure** `.env` is in `.gitignore` (it is by default in this repo).

---

## 🚀 How to Use

1. **Stage your changes** in any Git repository:
   ```bash
   git add <file1> <file2> ...
   ```
2. **Run the script** from your project’s root folder (the folder containing `main.py`):
   ```bash
   python main.py
   ```
3. You’ll see up to 3 suggested commit messages printed to the console, e.g.:
   ```
   Generating commit message suggestions...

   Here are your commit message suggestions:

   1. Fix crash when loading empty configuration file
   2. Refactor API client to use async/await
   3. Update dependencies and bump version to 1.2.0

   Enter the number of the suggestion to use (1-3), or press ENTER to type your own:
   ```
4. **Choose** a suggestion (by typing `1`, `2`, or `3`) or press ENTER to type a custom message.
5. **Confirm** whether to run `git commit -m "..."`. Type `y` to proceed or any other key to abort.

---

## ⚙️ File Overview

- **`.gitignore`** – ignores `.env`, `__pycache__/`, and other unwanted files.
- **`.env.example`** – template for your real `.env` (contains `OPENAI_API_KEY=…`).
- **`diff_reader.py`** – gets the staged diff (`git diff --cached`) as a string.
- **`openai_helper.py`** – calls the OpenAI API to convert that diff into commit-message suggestions.
- **`main.py`** – ties everything together, prompts the user, and optionally runs `git commit -m "…"`.
- **`requirements.txt`** – (optional) lists `openai` and `python-dotenv`.

---

## 💡 Tips & Next Steps

- If you want **more or fewer suggestions**, change `n_suggestions=3` in the call to `generate_commit_messages(...)` inside `main.py`.
- You can switch to **GPT-4** by editing the model name in `openai_helper.py`:
  ```py
  response = openai.ChatCompletion.create(
      model="gpt-4",
      ...
  )
  ```
- To make this run **automatically** as a Git hook (e.g. `prepare-commit-msg`), copy `main.py` logic into a script in `.git/hooks/prepare-commit-msg`, or call it from there.
- If you ever need to upgrade/downgrade dependencies, update `requirements.txt` and run `pip install -r requirements.txt`.

Enjoy faster, more consistent commit messages!
