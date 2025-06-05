# openai_helper.py

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("No OPENAI_API_KEY found. Make sure your .env file is set up.")

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_commit_messages(
    diff_text: str,
    file_list: list[str],
    n_suggestions: int = 3,
    model: str = "gpt-3.5-turbo"
):
    """
    Sends the diff and file list to OpenAI and returns:
    - list of commit suggestions
    - token usage stats
    """
    files_str = ", ".join(file_list) if file_list else "None"
    
    prompt = (
        f"Here is a Git diff and list of changed files.\n\n"
        f"Files changed: {files_str}\n\n"
        f"Git diff:\n{diff_text}\n\n"
        f"Generate exactly {n_suggestions} concise Git commit messages summarizing these changes. "
        f"Return them as a numbered list (1., 2., 3.)."
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an assistant that writes clear, helpful Git commit messages."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=300
        )
    except Exception as e:
        print("Error calling OpenAI API:", e)
        return [], 0, 0

    message_text = response.choices[0].message.content.strip()
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens

    # Parse lines that start with '1.', '2.', etc.
    suggestions = []
    for line in message_text.splitlines():
        line = line.strip()
        if line[:2] in {"1.", "2.", "3.", "4.", "5."}:  # basic safeguard
            cleaned = line[2:].strip()
            if cleaned:
                suggestions.append(cleaned)

    return suggestions[:n_suggestions], input_tokens, output_tokens
