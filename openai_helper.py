# openai_helper.py

import os
import openai
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("No OPENAI_API_KEY found in environment. Please create a .env file with your key.")

openai.api_key = OPENAI_API_KEY

def generate_commit_messages(diff_text: str, n_suggestions: int = 3) -> list[str]:
    """
    Given a git diff text, send it to OpenAI and return a list of commit message suggestions.
    - diff_text: the raw output of `git diff --cached`
    - n_suggestions: how many different commit messages to request
    """
    prompt = (
        "You are a helpful assistant that writes concise, descriptive Git commit messages.\n"
        "Below is the unified diff of staged changes (git diff --cached):\n\n"
        f"{diff_text}\n\n"
        "Based on these changes, suggest "
        f"{n_suggestions} commit message(s), each on its own line (do NOT include bullet characters).\n"
        "Be concise (e.g., 'Fix bug in user authentication')."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You generate Git commit messages."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200,
            n=1
        )
    except Exception as e:
        print("Error calling OpenAI API:", e)
        return []

    # Extract the assistant's reply text
    message_text = response.choices[0].message.content.strip()

    # Split into lines, strip any leading "- " or numbering if present
    suggestions = []
    for line in message_text.splitlines():
        clean = line.strip()
        # Remove common leading characters like "- ", "1. ", "• "
        if clean.startswith(("-", "•")):
            clean = clean.lstrip("-•").strip()
        if clean and not clean.lower().startswith("1") and not clean.lower().startswith("2") and not clean.lower().startswith("3"):
            # If the model tries numbering "1. Foo", strip "1."
            clean = clean.lstrip("1234567890. ").strip()
        if clean:
            suggestions.append(clean)

    return suggestions[:n_suggestions]
