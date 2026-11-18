
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

# Locate our project folder
BASE_DIR = Path(__file__).resolve().parent

# Load Groq API key
load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError("GROQ_API_KEY not found in .env")

# Initialize the Groq client
client = Groq(api_key=api_key)

# Use the recording from Step 5
audio_path = BASE_DIR / "recorded_audio.wav"

if not audio_path.exists():
    raise FileNotFoundError(
        "recorded_audio.wav not found. Run test_microphone.py first."
    )

print("Sending your audio to Whisper AI...")

# Send the audio to Whisper
with open(audio_path, "rb") as audio_file:
    transcription = client.audio.transcriptions.create(
        file=audio_file,
        model="whisper-large-v3-turbo",
        response_format="json",
        language="en"
    )

# Display the recognized speech
print("\nTranscription successful!")
print("You said:", transcription.text)
