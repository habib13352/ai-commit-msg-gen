# AI Commit Message Generator

A minimal CLI utility that reads your staged Git diff and uses OpenAI’s GPT-3.5 API to suggest clear, concise commit messages. It logs each invocation (diff, suggestions, chosen message, token usage, and estimated cost) for easy auditing.

<details>
<summary><strong>Prerequisites</strong></summary>

1. **Git** installed (so `git diff --cached` and `git commit` work)  
2. **Python 3.8+** installed  
3. An **OpenAI API Key** (from https://platform.openai.com/account/api-keys)

</details>

<details>
<summary><strong>Setup</strong></summary>

1. **Clone or download** this repository:
   ```bash
   git clone https://github.com/habib13352/ai-commit-msg-gen.git
   cd ai-commit-msg-gen
   ```

2. **Install dependencies**:
   ```bash
   pip install openai python-dotenv
   ```

3. **Copy `.env.example` to `.env`** and insert your API key:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` so it contains:
   ```
   OPENAI_API_KEY=sk-...
   ```

4. **Ensure** `.env` and `logs/` are listed in `.gitignore` (they are by default).

</details>

<details>
<summary><strong>How to Use</strong></summary>

1. **Stage your changes** in any Git repository:
   ```bash
   git add <file1> <file2> ...
   ```

2. **Run the script** from your repository’s root (where `main.py` lives):
   ```bash
   python main.py
   ```

3. **Pick or type a message**:
   - The tool displays up to 3 AI-generated suggestions.
   - Enter a number (`1`, `2`, `3`) to choose one, or press ENTER to type your own.
   - Confirm (`y`) to run `git commit -m "..."`, or any other key to abort.

</details>

<details>
<summary><strong>Logging & Cost Tracking</strong></summary>

- Each run writes to `logs/commit_log.txt`.  
- Logged data includes:
  - Timestamp
  - Full diff sent to GPT
  - All suggestions returned by GPT
  - Your selected commit message (or custom message)
  - Token usage (`prompt_tokens` and `completion_tokens`)
  - Estimated cost (based on GPT-3.5 pricing)

- **GPT-3.5 Pricing**:
  - $0.0015 per 1 000 input tokens
  - $0.0020 per 1 000 output tokens

Use these logs to monitor usage and budget.

</details>

<details>
<summary><strong>File Overview</strong></summary>

- **`main.py`**  
  - Orchestrates the CLI: reads staged diff, retrieves suggestions, logs details, and commits.

- **`diff_reader.py`**  
  - Runs `git diff --cached` with UTF-8 decoding and error replacement.

- **`openai_helper.py`**  
  - Sends the diff to OpenAI, strips any emojis, returns suggestions and token counts.

- **`.env.example`**  
  - Template for your `.env` file.

- **`requirements.txt`**  
  - Lists `openai` and `python-dotenv`.

- **`logs/commit_log.txt`**  
  - Auto-created folder and file for invocation logs.

</details>

<details>
<summary><strong>Example Log Entry (`logs/commit_log.txt`)</strong></summary>

```
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
```

</details>

<details>
<summary><strong>Future Improvements & Ideas</strong></summary>

- **Git Hook Integration**  
  Automatically run this tool as a `prepare-commit-msg` hook so you don’t need to invoke `python main.py` manually.

- **Command-Line Options**  
  Add flags like `--num-suggestions`, `--auto-commit`, `--dry-run`, or `--model` for flexibility.

- **Conventional Commit Style**  
  Allow users to choose "feat:", "fix:", or other prefixes in commit messages.

- **CLI Packaging**  
  Package as a Python package on PyPI (`pip install ai-commit-msg`) for global installation.

- **Log Analysis Script**  
  Provide a script to summarize token usage and cost over time.

- **Budget Alerts**  
  Warn or prevent usage when projected monthly cost exceeds a specified threshold.

</details>

<details>
<summary><strong>License</strong></summary>

MIT License — use, modify, and distribute freely.

</details>
