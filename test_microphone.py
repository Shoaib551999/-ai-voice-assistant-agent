
import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 16000
DURATION = 5

print("Available microphone devices:")
print(sd.query_devices())

print("\nRecording will start now.")
print("Speak into your microphone for 5 seconds.")

audio = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="float32"
)

sd.wait()

sf.write("recorded_audio.wav", audio, SAMPLE_RATE)

print("\nRecording completed!")
print("Audio saved as recorded_audio.wav")
