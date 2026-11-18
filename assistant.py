
import os
import tempfile

import sounddevice as sd
import soundfile as sf
import pyttsx3
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("Set OPENAI_API_KEY in your .env file")

client = OpenAI()
MODEL = os.getenv("OPENAI_MODEL", "gpt-6-luna")

SAMPLE_RATE = 16000
RECORD_SECONDS = 5

speaker = pyttsx3.init()
speaker.setProperty("rate", 175)

history = []

def record_audio():
    print("\nRecording for 5 seconds. Speak now...")

    recording = sd.rec(
        int(RECORD_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
    )
    sd.wait()

    with tempfile.NamedTemporaryFile(
        suffix=".wav", delete=False
    ) as temp:
        audio_path = temp.name

    sf.write(audio_path, recording, SAMPLE_RATE)
    return audio_path

def transcribe_audio(audio_path):
    try:
        with open(audio_path, "rb") as audio:
            result = client.audio.transcriptions.create(
                model="gpt-transcribe",
                file=audio,
            )
        return result.text.strip()
    finally:
        os.remove(audio_path)

def generate_response(user_message):
    conversation = history + [
        {"role": "user", "content": user_message}
    ]

    response = client.responses.create(
        model=MODEL,
        instructions=(
            "You are a helpful personal voice assistant. "
            "Respond naturally and concisely. "
            "Keep responses suitable for speaking aloud."
        ),
        input=conversation,
    )

    answer = response.output_text.strip()

    history.extend([
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": answer},
    ])

    return answer

def speak(text):
    speaker.say(text)
    speaker.runAndWait()

def main():
    print("AI Voice Assistant")
    print("Press Enter to record, or type q to quit.")
    print("Voice output is AI-generated.")

    while True:
        command = input("\nPress Enter to speak: ")

        if command.lower() == "q":
            print("Goodbye!")
            break

        try:
            audio_path = record_audio()
            message = transcribe_audio(audio_path)

            if not message:
                print("No speech detected.")
                continue

            print(f"You: {message}")

            if message.lower() in {
                "exit", "quit", "goodbye", "stop"
            }:
                speak("Goodbye!")
                break

            answer = generate_response(message)

            print(f"Assistant: {answer}")
            speak(answer)

        except Exception as error:
            print(f"Error: {error}")

if __name__ == "__main__":
    main()