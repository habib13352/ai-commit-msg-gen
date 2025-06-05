# main.py
# still working on it
# is it working well?

import argparse
import sys
import subprocess
import os
import json
from datetime import datetime

from diff_reader import get_staged_diff, extract_changed_files
from openai_helper import generate_commit_messages

def get_repo_info():
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
    log_dir = os.path.dirname(log_path)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(entry) + "\n")

def main():
    parser = argparse.ArgumentParser(description="AI Commit Message Generator")
    parser.add_argument("-n", "--num-suggestions", type=int, default=3)
    parser.add_argument("-m", "--model", type=str, default="gpt-3.5-turbo")
    parser.add_argument("--auto-commit", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--log-path", type=str, default="logs/commit_log.json")
    args = parser.parse_args()

    diff_text = get_staged_diff()
    changed_files = extract_changed_files(diff_text)

    if not diff_text.strip():
        print("No staged changes found. Please `git add <files>` before running this tool.")
        sys.exit(0)

    if args.dry_run:
        print("Diff to be sent to GPT:\n")
        print(diff_text)
        sys.exit(0)

    print(f"Using model: {args.model}, generating {args.num_suggestions} suggestions...")
    suggestions, input_tokens, output_tokens = generate_commit_messages(
        diff_text,
        changed_files=changed_files,
        n_suggestions=args.num_suggestions,
        model=args.model
    )

    if not suggestions:
        print("No suggestions returned from OpenAI. Exiting.")
        sys.exit(1)

    print("\nHere are your commit message suggestions:\n")
    for idx, msg in enumerate(suggestions, start=1):
        print(f"{idx}. {msg}")

    print("\nEnter the number of the suggestion to use (1-{0}), or press ENTER to type your own:".format(args.num_suggestions))
    user_choice = input(f"Choice [1-{args.num_suggestions} or ENTER]: ").strip()

    if user_choice.isdigit() and 1 <= int(user_choice) <= args.num_suggestions:
        index = int(user_choice) - 1
        final_message = suggestions[index]
    else:
        final_message = input("Enter your custom commit message: ").strip()
        if not final_message:
            print("No commit message provided. Exiting without committing.")
            sys.exit(0)

    repo_info = get_repo_info()
    timestamp = datetime.now().isoformat()
    cost_input = (input_tokens / 1000) * 0.0015
    cost_output = (output_tokens / 1000) * 0.002
    total_cost = cost_input + cost_output

    log_entry = {
        "timestamp": timestamp,
        "repo": repo_info.get("repo", ""),
        "branch": repo_info.get("branch", ""),
        "diff": diff_text,
        "changed_files": changed_files,
        "suggestions": suggestions,
        "chosen_message": final_message,
        "tokens": {"input": input_tokens, "output": output_tokens},
        "cost_usd": round(total_cost, 6),
        "model": args.model
    }
    write_log_entry(args.log_path, log_entry)

    if args.auto_commit:
        print(f"Auto-commit enabled. Committing with message: {final_message}")
        try:
            subprocess.run(["git", "commit", "-m", final_message], check=True)
            print("✅ Commit created successfully.")
        except subprocess.CalledProcessError as e:
            print("Error running git commit:", e)
            sys.exit(1)
    else:
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
