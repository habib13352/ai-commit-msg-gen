# diff_reader.py

import subprocess
import sys

def get_staged_diff() -> str:
    """
    Runs `git diff --cached` to retrieve the unified diff of all staged changes.
    Returns the raw diff string. If an error occurs, prints to stderr and exits.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--cached"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",   # Force UTF-8 decoding
            errors="replace",   # Replace any undecodable characters
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print("❌ Error retrieving staged diff:", e.stderr, file=sys.stderr)
        sys.exit(1)
