
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

# Load the API key from the .env file
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError("GROQ_API_KEY not found in .env")

# Initialize Groq client
client = Groq(api_key=api_key)

# Send a test question to the AI

response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "system",
            "content": "You are a friendly personal AI assistant."
        },
        {
            "role": "user",
            "content": "Hello! Introduce yourself in two sentences."
        }
    ],
    reasoning_effort="low",
    max_completion_tokens=500
)


print("AI Response:")
print(response.choices[0].message.content)
