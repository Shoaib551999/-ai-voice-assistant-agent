
import pyttsx3

engine = pyttsx3.init()

# Configure the assistant's voice
engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)

print("Testing AI voice output...")

engine.say(
    "Hello! I am your personal AI voice assistant. "
    "I can now speak to you."
)

engine.runAndWait()

print("Speech test completed!")
