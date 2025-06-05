# diff_reader.py

import subprocess
import sys

def get_staged_diff() -> str:
    """
    Runs `git diff --cached` to retrieve the unified diff of all staged changes.
    Returns the raw diff string. If an error occurs, prints to stderr and exits.
    """
    try:
        completed_process = subprocess.run(
            ["git", "diff", "--cached"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        diff_text = completed_process.stdout
        return diff_text
    except subprocess.CalledProcessError as e:
        print("Error retrieving staged diff:", e.stderr, file=sys.stderr)
        sys.exit(1)
