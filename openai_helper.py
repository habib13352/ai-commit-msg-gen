# openai_helper.py

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from a ".env" file in the project root
load_dotenv()

# Read the OpenAI API key from the environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("No OPENAI_API_KEY found. Make sure your .env file is set up.")

# Initialize the OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_commit_messages(diff_text: str, changed_files: list = None, n_suggestions: int = 3, model: str = "gpt-3.5-turbo"):
    # Format the list of changed files for the prompt
    file_list_text = "\n".join(f"- {f}" for f in changed_files) if changed_files else "N/A"

    # Improved prompt for grouped, meaningful commit messages
    prompt = (
        "You are a professional assistant that writes clear, concise Git commit messages "
        "based on a staged diff and the changed filenames.\n\n"
        "Here are the staged files:\n"
        f"{file_list_text}\n\n"
        "Here is the unified diff of staged changes (git diff --cached):\n\n"
        f"{diff_text}\n\n"
        "Generate commit messages that summarize the purpose of all these changes together, "
        "as a single grouped commit.\n"
        "Avoid repeating individual filenames. Instead, capture the *intent* of the grouped change.\n\n"
        "Examples of good grouped commit messages:\n"
        "- Refactor logging system and update usage docs\n"
        "- Fix validation logic and improve error messages in API handlers\n"
        "- Update configuration and helper utilities for deployment\n\n"
        f"Now, based on these changes, suggest {n_suggestions} concise commit message(s), "
        "each on its own line with no bullets or emojis."
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You generate Git commit messages without emojis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=200
        )
    except Exception as e:
        print("Error calling OpenAI API:", e)
        return [], 0, 0

    message_text = response.choices[0].message.content.strip()
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens

    # Clean up and filter message lines
    suggestions = []
    for line in message_text.splitlines():
        clean = line.strip().lstrip("-•1234567890. ").strip()
        if clean:
            suggestions.append(clean)

    return suggestions[:n_suggestions], input_tokens, output_tokens
