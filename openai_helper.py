# openai_helper.py

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("No OPENAI_API_KEY found. Make sure your .env file is set up.")

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_commit_messages(diff_text: str, changed_files: list = None, n_suggestions: int = 3, model: str = "gpt-3.5-turbo"):
    file_list_text = "\n".join(f"- {f}" for f in changed_files) if changed_files else "N/A"

    prompt = (
        "You are a professional assistant that writes clear, concise Git commit messages "
        "based on a staged diff and file names. Do NOT include any emojis or bullet points.\n\n"
        f"Changed files:\n{file_list_text}\n\n"
        "Below is the unified diff of staged changes (git diff --cached):\n\n"
        f"{diff_text}\n\n"
        f"Based on these changes, suggest {n_suggestions} commit message(s), "
        "each on its own line without any emojis or numbering."
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

    suggestions = []
    for line in message_text.splitlines():
        clean = line.strip().lstrip("-•1234567890. ").strip()
        if clean:
            suggestions.append(clean)

    return suggestions[:n_suggestions], input_tokens, output_tokens
