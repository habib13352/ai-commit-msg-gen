# diff_reader.py
# so far this is working

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
            encoding="utf-8",
            errors="replace",
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print("❌ Error retrieving staged diff:", e.stderr, file=sys.stderr)
        sys.exit(1)

def extract_changed_files(diff: str) -> list:
    """
    Parses the diff output to get a list of changed file paths.
    """
    files = set()
    for line in diff.splitlines():
        if line.startswith("diff --git"):
            parts = line.split()
            # Extract up to the two file paths following 'diff --git'
            for path in parts[2:4]:
                if path.startswith(("a/", "b/")):
                    files.add(path[2:])
                else:
                    files.add(path)
    return sorted(files)
