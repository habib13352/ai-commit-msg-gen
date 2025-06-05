# openai_helper.py

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from a ".env" file in the project root
load_dotenv()

# Read the OpenAI API key from the environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    # If no key is found, raise an error immediately
    raise ValueError("No OPENAI_API_KEY found. Make sure your .env file is set up.")

# Initialize the OpenAI client (version 1.x syntax)
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_commit_messages(diff_text: str, n_suggestions: int = 3, model: str = "gpt-3.5-turbo"):
    """
    1) Builds a prompt that tells the model it is a Git-commit-message generator.
    2) Sends the prompt (including the staged diff) to OpenAI's chat completion endpoint.
    3) Parses the response, pulling out up to n_suggestions lines.
    4) Returns a tuple: (suggestions_list, input_tokens_count, output_tokens_count).

    Parameters:
      - diff_text: the full "git diff --cached" output as a string
      - n_suggestions: how many commit messages to ask for (default: 3)
      - model: the OpenAI model to use ("gpt-3.5-turbo" by default)

    Returns:
      ([suggestion1, suggestion2, ...], input_tokens, output_tokens)
      If an error happens, returns ([], 0, 0).
    """
    # Build the multi-line user prompt
    prompt = (
        "You are a professional assistant that writes clear, concise Git commit messages "
        "based on a staged diff. Do NOT include any emojis or bullet points—just plain text.\n"
        "Below is the unified diff of staged changes (git diff --cached):\n\n"
        f"{diff_text}\n\n"
        f"Based on these changes, suggest {n_suggestions} commit message(s), "
        "each on its own line without any emojis or numbering."
    )

    try:
        # Call the chat completion endpoint with temperature=0 for deterministic output
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
        # Print any API errors and return empty results
        print("Error calling OpenAI API:", e)
        return [], 0, 0

    # The model's reply is under response.choices[0].message.content
    message_text = response.choices[0].message.content.strip()

    # Record token usage for cost tracking
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens

    # Split the response into lines, strip numbers/bullets, and collect non-empty lines
    suggestions = []
    for line in message_text.splitlines():
        # Remove leading numbers (e.g., "1. ") or bullet characters ("-", "•", etc.)
        clean = line.strip().lstrip("-•1234567890. ").strip()
        if clean:
            suggestions.append(clean)

    # Only return up to n_suggestions items in case the model returned more
    return suggestions[:n_suggestions], input_tokens, output_tokens
