# main.py

import argparse
import sys
import subprocess
import os
import json
from datetime import datetime

from diff_reader import get_staged_diff
from openai_helper import generate_commit_messages

def get_repo_info():
    """
    Returns a dict with repository name and current branch.
    If not in a Git repo, returns empty strings.
    """
    try:
        repo_path = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=True
        ).stdout.strip()
        repo_name = os.path.basename(repo_path)
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=True
        ).stdout.strip()
        return {"repo": repo_name, "branch": branch}
    except subprocess.CalledProcessError:
        return {"repo": "", "branch": ""}


def write_log_entry(log_path, entry):
    """
    Appends a JSON entry (as one line) to the log file.
    """
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(entry) + "\n")


def get_staged_file_list():
    """
    Returns a list of staged filenames (git diff --cached --name-only).
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=True
        )
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except subprocess.CalledProcessError:
        return []


def confirm(prompt_text):
    return input(f"{prompt_text} (y/N): ").strip().lower() == "y"


def main():
    parser = argparse.ArgumentParser(description="AI Commit Message Generator")
    parser.add_argument(
        "-n", "--num-suggestions",
        type=int,
        default=3,
        help="Number of commit message suggestions to generate (default: 3)"
    )
    parser.add_argument(
        "-m", "--model",
        type=str,
        default="gpt-3.5-turbo",
        help="OpenAI model to use (e.g., gpt-3.5-turbo, gpt-4)"
    )
    parser.add_argument(
        "--auto-commit",
        action="store_true",
        help="Automatically run 'git commit' with the selected message (skip prompt)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print suggestions without calling OpenAI or committing"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show token usage and cost after suggestions"
    )
    parser.add_argument(
        "--log-path",
        type=str,
        default="logs/commit_log.json",
        help="Path to the JSON log file (default: logs/commit_log.json)"
    )

    args = parser.parse_args()

    # 1. Get the staged diff
    diff_text = get_staged_diff()
    if not diff_text.strip():
        print("No staged changes found. Please `git add <files>` before running this tool.")
        sys.exit(0)

    # 1a. Also grab the list of staged filenames
    file_list = get_staged_file_list()

    # 2. If dry run, print diff + files and exit
    if args.dry_run:
        print("DRY RUN MODE\n")
        print("Files changed:", ", ".join(file_list) if file_list else "None")
        print("\nDiff:\n", diff_text)
        sys.exit(0)

    # 3. Generate suggestions
    print(f"Using model: {args.model}, generating {args.num_suggestions} suggestions...\n")
    suggestions, input_tokens, output_tokens = generate_commit_messages(
        diff_text,
        file_list=file_list,
        n_suggestions=args.num_suggestions,
        model=args.model
    )
    if not suggestions:
        print("No suggestions returned. Aborting.")
        sys.exit(1)

    # 4. Show suggestions
    print("Here are your commit message suggestions:\n")
    for idx, msg in enumerate(suggestions, start=1):
        print(f"{idx}. {msg}")

    # 5. Prompt user to choose one or type their own
    user_choice = input(f"\nEnter 1-{args.num_suggestions} to select a suggestion, or press ENTER to type your own: ").strip()
    if user_choice.isdigit() and 1 <= int(user_choice) <= args.num_suggestions:
        final_message = suggestions[int(user_choice) - 1]
    else:
        final_message = input("Type your custom commit message: ").strip()
        if not final_message:
            print("No commit message provided. Exiting.")
            sys.exit(0)

    # 6. Prepare and write log
    repo_info = get_repo_info()
    timestamp = datetime.now().isoformat()
    cost_input = (input_tokens / 1000) * 0.0015
    cost_output = (output_tokens / 1000) * 0.002
    total_cost = round(cost_input + cost_output, 6)

    log_entry = {
        "timestamp": timestamp,
        "repo": repo_info.get("repo", ""),
        "branch": repo_info.get("branch", ""),
        "files_changed": file_list,
        "diff": diff_text,
        "suggestions": suggestions,
        "chosen_message": final_message,
        "tokens": {"input": input_tokens, "output": output_tokens},
        "cost_usd": total_cost,
        "model": args.model
    }
    write_log_entry(args.log_path, log_entry)

    if args.verbose:
        print(f"\nToken usage: {input_tokens} input, {output_tokens} output → Cost: ${total_cost:.6f}")

    # 7. Confirm and run git commit
    if args.auto_commit or confirm(f"\nRun: git commit -m \"{final_message}\"?"):
        try:
            subprocess.run(["git", "commit", "-m", final_message], check=True)
            print("✅ Commit created.")
        except subprocess.CalledProcessError as e:
            print("Error running git commit:", e)
    else:
        print("Commit aborted.")

if __name__ == "__main__":
    main()
