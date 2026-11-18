import pyttsx3
import os
from pathlib import Path

import sounddevice as sd
import soundfile as sf
from dotenv import load_dotenv
from groq import Groq

# -----------------------------
# 1. Load configuration
# -----------------------------

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError("GROQ_API_KEY not found in .env")

client = Groq(api_key=api_key)
conversation_history = [
    {
        "role": "system",
        "content": (
            "You are a friendly AI personal voice assistant. "
            "Remember the conversation context and answer "
            "questions naturally, clearly, and concisely."
        )
    }
]

# -----------------------------
# 2. Audio configuration
# -----------------------------

SAMPLE_RATE = 16000
DURATION = 5
AUDIO_FILE = BASE_DIR / "recorded_audio.wav"

# -----------------------------
# 3. Record your voice
# -----------------------------

def record_voice():
    print("\nRecording started. Speak now!")

    audio = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32"
    )

    sd.wait()

    sf.write(AUDIO_FILE, audio, SAMPLE_RATE)

    print("Recording completed!")


# -----------------------------
# 4. Convert speech to text
# -----------------------------

def speech_to_text():
    print("\nTranscribing your voice...")

    with open(AUDIO_FILE, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            file=audio_file,
            response_format="json",
            language="en"
        )

    return transcription.text.strip()


# -----------------------------
# 5. Generate AI response
# -----------------------------


def generate_ai_response(user_text):
    print("\nAI is thinking...")

    conversation_history.append({
        "role": "user",
        "content": user_text
    })

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=conversation_history,
            reasoning_effort="low",
            max_completion_tokens=500
        )

        ai_response = (
            response.choices[0].message.content or ""
        ).strip()

        if not ai_response:
            raise RuntimeError("AI returned an empty response.")

        conversation_history.append({
            "role": "assistant",
            "content": ai_response
        })

        return ai_response

    except Exception:
        # Remove the unanswered question from history
        conversation_history.pop()
        raise

# -----------------------------
# 6. Main application
# -----------------------------


def main():
    print("================================")
    print("      AI VOICE ASSISTANT")
    print("================================")
    print("Press Enter to speak.")
    print("Type q to quit.")

    while True:
        command = input("\nPress Enter to record: ")

        if command.strip().lower() == "q":
            speak_response("Goodbye! See you soon.")
            break

        try:
            record_voice()

            user_text = speech_to_text()

            if not user_text:
                print("No speech detected. Try again.")
                continue

            print("\nYou:", user_text)

            if user_text.lower().strip(" .!?") in [
                "exit", "quit", "goodbye", "stop assistant"
            ]:
                speak_response("Goodbye!")
                break

            ai_response = generate_ai_response(user_text)

            print("\nAI Assistant:", ai_response)

            speak_response(ai_response)

        except Exception as error:
            print("\nError:", error)
            print("Please try again.")


# -----------------------------
# Text-to-Speech
# -----------------------------

def speak_response(text):
    print("\nAssistant is speaking...")

    engine = pyttsx3.init()
    engine.setProperty("rate", 175)
    engine.setProperty("volume", 1.0)

    engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    main()



