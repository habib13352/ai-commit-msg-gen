# openai_helper.py

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Read API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("No OPENAI_API_KEY found. Make sure your .env file is set up.")

# Initialize OpenAI client (new v1.x syntax)
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_commit_messages(diff_text: str, n_suggestions: int = 3):
    """
    Sends diff to OpenAI and returns:
    - list of suggestions
    - input_tokens, output_tokens for cost tracking
    """
    prompt = (
        "You are a helpful assistant that writes concise, descriptive Git commit messages.\n"
        "Below is the unified diff of staged changes (git diff --cached):\n\n"
        f"{diff_text}\n\n"
        f"Based on these changes, suggest {n_suggestions} commit message(s), "
        "each on its own line without bullet points or numbering. Be brief and informative."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You generate Git commit messages."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
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
