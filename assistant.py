"""
assistant.py
Main orchestrator – ties together voice I/O, NLP, and command execution.
"""

import sys
import string
import pickle
import os



from model_trainer   import load_model, preprocess
from command_executor import execute, INTENT_HANDLERS
from voice_io        import speak, listen

WAKE_WORDS  = {"hey assistant", "hello assistant", "assistant", "wake up"}
QUIT_WORDS  = {"quit", "exit", "bye", "goodbye", "stop", "shut up"}
CONFIDENCE_THRESHOLD = 0.40   # below this → ask user to repeat


class VoiceAssistant:
    def __init__(self):
        self.model = load_model()
        self.running = False

    # ── NLP pipeline ─────────────────────────────────────────────────────
    def predict_intent(self, text: str):
        """Return (intent_label, confidence) for *text*."""
        processed = preprocess(text)
        proba = self.model.predict_proba([processed])[0]
        classes = self.model.classes_
        idx = proba.argmax()
        return classes[idx], proba[idx]

    # ── Main loop ─────────────────────────────────────────────────────────
    def run(self, continuous: bool = True):
        """
        Continuous loop: listen → classify → execute → respond.
        Set continuous=False for a single-shot interaction (useful in tests).
        """
        self.running = True
        speak("Voice Assistant is ready. Say a command or type it below.")

        while self.running:
            text = listen()

            if text is None:
                continue

            text_lower = text.lower().strip()

            # Quit check
            if any(q in text_lower for q in QUIT_WORDS):
                speak("Goodbye! Have a great day.")
                self.running = False
                break

            # Predict
            intent, confidence = self.predict_intent(text)
            print(f"[Assistant] Intent: '{intent}'  Confidence: {confidence:.2%}")

            if confidence < CONFIDENCE_THRESHOLD:
                speak("I'm not sure what you meant. Could you please repeat that?")
                if not continuous:
                    break
                continue

            # Execute
            response = execute(intent)
            speak(response)

            if not continuous:
                break

    # ── Single-command convenience method ─────────────────────────────────
    def process_command(self, text: str) -> dict:
        """Process a text command and return a result dict (no audio)."""
        intent, confidence = self.predict_intent(text)
        return {
            "input":      text,
            "intent":     intent,
            "confidence": round(float(confidence), 4),
            "response":   execute(intent) if confidence >= CONFIDENCE_THRESHOLD
                          else "Low confidence – please rephrase.",
        }


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────
if __name__ == "__main__":
    assistant = VoiceAssistant()
    try:
        assistant.run(continuous=True)
    except KeyboardInterrupt:
        print("\n[Assistant] Interrupted by user.")
        speak("Shutting down. Goodbye!")
