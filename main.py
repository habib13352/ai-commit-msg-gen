# main.py

import sys
import subprocess

from diff_reader import get_staged_diff
from openai_helper import generate_commit_messages

def main():
    # 1. Get the staged diff
    diff_text = get_staged_diff()
    if not diff_text.strip():
        print("No staged changes found. Please `git add <files>` before running this tool.")
        sys.exit(0)

    # 2. Generate commit message suggestions
    print("\nGenerating commit message suggestions...\n")
    suggestions = generate_commit_messages(diff_text, n_suggestions=3)
    if not suggestions:
        print("No suggestions returned from OpenAI. Exiting.")
        sys.exit(1)

    # 3. Show suggestions
    print("Here are your commit message suggestions:\n")
    for idx, msg in enumerate(suggestions, start=1):
        print(f"{idx}. {msg}")

    # 4. Ask the user to pick one or type a custom message
    print("\nEnter the number of the suggestion to use (1-3), or press ENTER to type your own:")
    user_choice = input("Choice [1-3 or ENTER]: ").strip()

    if user_choice in {"1", "2", "3"}:
        index = int(user_choice) - 1
        final_message = suggestions[index]
    else:
        final_message = input("Enter your custom commit message: ").strip()
        if not final_message:
            print("No commit message provided. Exiting without committing.")
            sys.exit(0)

    # 5. Confirm and run git commit
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
