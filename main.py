# main.py
# test 1, will it work off the rip?
# no, what about test 2? YES!

import sys
import subprocess
import os
from datetime import datetime

from diff_reader import get_staged_diff
from openai_helper import generate_commit_messages

def main():
    # 1. Get the staged diff
    diff_text = get_staged_diff()
    if not diff_text.strip():
        print("No staged changes found. Please `git add <files>` before running this tool.")
        sys.exit(0)

    # 2. Generate commit message suggestions and token stats
    print("\nGenerating commit message suggestions...\n")
    suggestions, input_tokens, output_tokens = generate_commit_messages(diff_text, n_suggestions=3)
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

    # 5. Log everything to logs/commit_log.txt
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_folder = "logs"
    os.makedirs(log_folder, exist_ok=True)
    log_path = os.path.join(log_folder, "commit_log.txt")

    cost_input = (input_tokens / 1000) * 0.0015  # $0.0015 / 1K input tokens
    cost_output = (output_tokens / 1000) * 0.002  # $0.002 / 1K output tokens
    total_cost = cost_input + cost_output

    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"\n---\n🕒 Timestamp: {timestamp}\n")
        log_file.write("📄 Diff Sent to GPT:\n")
        log_file.write(diff_text.strip() + "\n\n")
        log_file.write("🤖 GPT Suggestions:\n")
        for i, s in enumerate(suggestions, 1):
            log_file.write(f"{i}. {s}\n")
        log_file.write(f"\n✅ Selected Commit Message: {final_message}\n")
        log_file.write(f"\n📊 Token Usage: {input_tokens} input, {output_tokens} output\n")
        log_file.write(f"💸 Estimated Cost: ${total_cost:.6f}\n")

    # 6. Confirm and run git commit
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
