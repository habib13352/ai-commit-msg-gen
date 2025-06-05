# main.py

import argparse
import sys
import subprocess
import os
import json
from datetime import datetime

# Import your helper functions:
# - get_staged_diff() reads the current staged diff via "git diff --cached"
# - generate_commit_messages() calls the OpenAI API and returns suggestions + token usage
from diff_reader import get_staged_diff
from openai_helper import generate_commit_messages


def get_repo_info():
    """
    Returns a dictionary containing:
      - 'repo': the repository’s top-level folder name
      - 'branch': the current Git branch name
    If the current working directory isn’t a Git repo, it returns {"repo": "", "branch": ""}.
    """
    try:
        # Run "git rev-parse --show-toplevel" to find the top-level path of the repo
        repo_path = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,  # ignore errors (e.g., not a Git repo)
            text=True,                   # return result.stdout as str
            check=True
        ).stdout.strip()

        # Extract just the folder name from the full path
        repo_name = os.path.basename(repo_path)

        # Run "git rev-parse --abbrev-ref HEAD" to get the current branch name
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=True
        ).stdout.strip()

        return {"repo": repo_name, "branch": branch}

    except subprocess.CalledProcessError:
        # If any command fails (e.g., not in a Git repo), return empty values
        return {"repo": "", "branch": ""}


def write_log_entry(log_path, entry):
    """
    Appends a single JSON object (as one line) to the specified log file.
    - log_path: path to the JSON log file (e.g., "logs/commit_log.json")
    - entry: Python dict to write as JSON
    Creates the parent folder if it doesn’t exist.
    """
    # Ensure the directory for the log file exists
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    # Append the JSON entry to the log file, followed by a newline
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(entry) + "\n")


def main():
    # 1. Set up command-line arguments with argparse
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
        "--log-path",
        type=str,
        default="logs/commit_log.json",
        help="Path to the JSON log file (default: logs/commit_log.json)"
    )

    # Parse the arguments into the "args" namespace
    args = parser.parse_args()

    # 2. Retrieve the unified diff of all staged changes
    diff_text = get_staged_diff()
    if not diff_text.strip():
        # If there are no staged changes, inform the user and exit cleanly
        print("No staged changes found. Please `git add <files>` before running this tool.")
        sys.exit(0)

    # 3. If the user passed --dry-run, just print the diff and exit
    if args.dry_run:
        print("Diff to be sent to GPT:\n")
        print(diff_text)
        sys.exit(0)

    # 4. Call the OpenAI helper to generate commit message suggestions
    #    It returns (suggestions, input_tokens, output_tokens).
    print(f"Using model: {args.model}, generating {args.num_suggestions} suggestions...")
    suggestions, input_tokens, output_tokens = generate_commit_messages(
        diff_text,
        n_suggestions=args.num_suggestions,
        model=args.model
    )

    # If the OpenAI call failed or returned no suggestions, exit
    if not suggestions:
        print("No suggestions returned from OpenAI. Exiting.")
        sys.exit(1)

    # 5. Display the suggestions to the user
    print("\nHere are your commit message suggestions:\n")
    for idx, msg in enumerate(suggestions, start=1):
        print(f"{idx}. {msg}")

    # 6. Prompt the user to choose one suggestion or type their own
    print("\nEnter the number of the suggestion to use (1-{0}), or press ENTER to type your own:".format(args.num_suggestions))
    user_choice = input(f"Choice [1-{args.num_suggestions} or ENTER]: ").strip()

    # If they typed a valid number, use that suggestion; otherwise, prompt for custom message
    if user_choice.isdigit() and 1 <= int(user_choice) <= args.num_suggestions:
        index = int(user_choice) - 1
        final_message = suggestions[index]
    else:
        final_message = input("Enter your custom commit message: ").strip()
        if not final_message:
            # If they hit ENTER without typing anything, we exit without committing
            print("No commit message provided. Exiting without committing.")
            sys.exit(0)

    # 7. Prepare a log entry with metadata, token usage, etc.
    repo_info = get_repo_info()
    timestamp = datetime.now().isoformat()

    # Cost estimation for GPT-3.5:
    # $0.0015 per 1K input tokens, $0.002 per 1K output tokens
    cost_input = (input_tokens / 1000) * 0.0015
    cost_output = (output_tokens / 1000) * 0.002
    total_cost = cost_input + cost_output

    log_entry = {
        "timestamp": timestamp,
        "repo": repo_info.get("repo", ""),
        "branch": repo_info.get("branch", ""),
        "diff": diff_text,
        "suggestions": suggestions,
        "chosen_message": final_message,
        "tokens": {"input": input_tokens, "output": output_tokens},
        "cost_usd": round(total_cost, 6),
        "model": args.model
    }
    write_log_entry(args.log_path, log_entry)

    # 8. Finally, either auto-commit or prompt for confirmation
    if args.auto_commit:
        # If --auto-commit was set, skip the prompt and run git commit immediately
        print(f"Auto-commit enabled. Committing with message: {final_message}")
        try:
            subprocess.run(["git", "commit", "-m", final_message], check=True)
            print("✅ Commit created successfully.")
        except subprocess.CalledProcessError as e:
            print("Error running git commit:", e)
            sys.exit(1)
    else:
        # Otherwise, show the exact git command and ask for "y/N"
        print(f"\nAbout to run:\n    git commit -m \"{final_message}\"\n")
        run_commit = input("Proceed with commit? (y/N): ").strip().lower()
        if run_commit == "y":
            try:
                subprocess.run(["git", "commit", "-m", final_message], check=True)
                print("✅ Commit created successfully.")
            except subprocess.CalledProcessError as e:
                print("Error running git commit:", e)
                sys.exit(1)
        else:
            print("Aborted. You can manually commit using the suggested message.")


if __name__ == "__main__":
    main()
