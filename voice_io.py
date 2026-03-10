"""
voice_io.py
Handles microphone input (speech → text) and speaker output (text → speech).
"""

import sys

# ── Speech Recognition ──────────────────────────────────────────────────────
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False
    print("[VoiceIO] WARNING: SpeechRecognition not installed. "
          "Falling back to keyboard input.")

# ── Text-to-Speech ───────────────────────────────────────────────────────────
try:
    import pyttsx3
    _tts_engine = pyttsx3.init()
    _tts_engine.setProperty("rate", 160)   # words per minute
    _tts_engine.setProperty("volume", 0.9)
    TTS_AVAILABLE = True
except Exception:
    TTS_AVAILABLE = False
    print("[VoiceIO] WARNING: pyttsx3 not available. Using print for feedback.")


# ──────────────────────────────────────────────
# Text-to-Speech
# ──────────────────────────────────────────────
def speak(text: str):
    """Convert *text* to audible speech (or print if TTS unavailable)."""
    print(f"[Assistant] {text}")
    if TTS_AVAILABLE:
        try:
            _tts_engine.say(text)
            _tts_engine.runAndWait()
        except Exception as e:
            print(f"[VoiceIO] TTS error: {e}")


# ──────────────────────────────────────────────
# Speech-to-Text
# ──────────────────────────────────────────────
def listen(timeout: int = 5, phrase_limit: int = 8) -> str | None:
    """
    Listen via microphone and return the recognised text, or None on failure.
    Falls back to keyboard input when SpeechRecognition is unavailable.
    """
    if not SR_AVAILABLE:
        return _keyboard_fallback()

    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True

    try:
        with sr.Microphone() as source:
            print("[VoiceIO] Adjusting for ambient noise …")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("[VoiceIO] Listening …")
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_limit,
            )
    except sr.WaitTimeoutError:
        print("[VoiceIO] No speech detected within timeout.")
        return None
    except Exception as e:
        print(f"[VoiceIO] Microphone error: {e}")
        return _keyboard_fallback()

    # Try Google Web Speech API first (free, no key needed)
    try:
        text = recognizer.recognize_google(audio)
        print(f"[VoiceIO] Heard: '{text}'")
        return text
    except sr.UnknownValueError:
        speak("Sorry, I could not understand that. Could you repeat?")
        return None
    except sr.RequestError as e:
        print(f"[VoiceIO] Google API error ({e}). Trying offline …")
        return _offline_fallback(recognizer, audio)


def _offline_fallback(recognizer, audio) -> str | None:
    """Try sphinx offline recognition."""
    try:
        text = recognizer.recognize_sphinx(audio)
        print(f"[VoiceIO] Heard (offline): '{text}'")
        return text
    except Exception:
        speak("Speech service unavailable. Please type your command.")
        return _keyboard_fallback()


def _keyboard_fallback() -> str | None:
    """Read command from stdin when mic/SR is not available."""
    try:
        cmd = input("Type command (or 'quit'): ").strip()
        return cmd if cmd else None
    except (EOFError, KeyboardInterrupt):
        return None
