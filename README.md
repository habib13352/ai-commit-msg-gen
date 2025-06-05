AI Commit Message Generator
===========================

A minimal CLI utility that reads your staged Git diff and uses OpenAI’s GPT-3.5 API to suggest clear, concise commit messages.

Each run logs details (diff, suggestions, chosen message, token usage, cost) for easy auditing and tracking.

------------------------------------------------------------

📦 Prerequisites
----------------
- Git installed (so `git diff --cached` and `git commit` work)
- Python 3.8+
- OpenAI API key — Get yours from: https://platform.openai.com/account/api-keys

------------------------------------------------------------

⚙️ Setup
--------
1. Clone the repo:
   git clone https://github.com/habib13352/ai-commit-msg-gen.git
   cd ai-commit-msg-gen

2. Install dependencies:
   pip install openai python-dotenv

3. Set up your `.env` file:
   cp .env.example .env

   Then edit `.env` and insert your API key:
   OPENAI_API_KEY=sk-...

4. Ensure `.env` and the `logs/` folder are listed in `.gitignore`.

------------------------------------------------------------

🚀 How to Use
-------------
1. Stage your changes:
   git add <file1> <file2> ...

2. Run the script:
   python main.py

3. Choose your commit message:
   - Up to 3 AI suggestions will be shown.
   - Enter `1`, `2`, or `3` to pick a suggestion, or press ENTER to type your own.
   - Press `y` to confirm and commit, or any other key to cancel.

------------------------------------------------------------

🧾 Logging & Cost Tracking
--------------------------
Each run appends a log to `logs/commit_log.json` containing:

- Timestamp
- Git diff sent to GPT
- Suggestions returned
- Selected message
- Token usage (prompt_tokens, completion_tokens)
- Estimated cost

GPT-3.5 Pricing (as of June 2025):
- $0.0015 per 1,000 input tokens
- $0.0020 per 1,000 output tokens

------------------------------------------------------------

📁 File Overview
----------------
- main.py              → Core CLI logic: reads diffs, prompts GPT, logs, commits
- diff_reader.py       → Gets UTF-8 decoded Git staged diff safely
- openai_helper.py     → Handles OpenAI API calls, ensures commit messages contain no emojis, returns suggestions
- .env.example         → Example environment file with placeholder key
- requirements.txt     → Required Python packages
- logs/commit_log.json → Stores commit suggestion logs and cost tracking

------------------------------------------------------------

📝 Example Log Entry
--------------------
---
Timestamp: 2025-06-05 10:15:22
Diff Sent to GPT:
diff --git a/main.py b/main.py
index 123abc..456def 100644
--- a/main.py
+++ b/main.py
@@ -10,6 +10,8 @@ def main():
     diff_text = get_staged_diff()

GPT Suggestions:
1. Add logging for commit details and cost estimation
2. Remove emojis from commit messages
3. Update diff_reader to use UTF-8 decoding

Selected Commit Message: Add logging for commit details and cost estimation

Token Usage: 134 input, 42 output
Estimated Cost: $0.000339

------------------------------------------------------------

🔮 Future Improvements (WIP)
----------------------
- Git Hook Integration (e.g. prepare-commit-msg)
- Command-line options: --num-suggestions, --auto-commit, --dry-run
- Conventional commit support: feat:, fix:, etc.
- CLI packaging for pip (e.g. pip install ai-commit-msg)
- Log analyzer for usage/cost trends
- Budget alerts for monthly cost caps

------------------------------------------------------------

📜 License
----------
MIT License — free to use, modify, and distribute.