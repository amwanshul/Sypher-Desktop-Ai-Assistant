"""
assistant.py  v3
Main orchestrator – ties together voice I/O, LLM, NLP, slot extraction,
and command execution.

v3: LLM-first command understanding with ML classifier fallback.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model_trainer    import load_model, preprocess, train
from command_executor import execute, INTENT_HANDLERS, save_dynamic_command
from slot_extractor   import extract_slots
from llm_engine       import llm_understand, llm_available
from dataset          import add_to_dataset
from voice_io         import speak, listen

WAKE_WORDS  = {"hey assistant", "hello assistant", "assistant", "wake up",
               "hey sypher", "sypher", "wake up sypher"}
QUIT_WORDS  = {"quit", "exit", "bye", "goodbye", "stop", "shut up"}
CONFIDENCE_THRESHOLD = 0.40


class VoiceAssistant:
    def __init__(self):
        self.model   = load_model()
        self.running = False
        self._phrase_cnt = 0

    # ── NLP pipeline (ML fallback) ───────────────────────────────
    def predict_intent(self, text: str):
        """Return (intent_label, confidence) via the ML classifier."""
        processed = preprocess(text)
        proba   = self.model.predict_proba([processed])[0]
        classes = self.model.classes_
        idx     = proba.argmax()
        return classes[idx], float(proba[idx])

    # ── Unified command processing (LLM-first) ──────────────────
    def process_command(self, text: str) -> dict:
        """
        Process a text command end-to-end:
          1. Try LLM (Gemini) for intent + slot extraction
          2. Fall back to ML classifier + regex slot extraction
          3. Execute the handler
          4. Return a result dict
        """
        # ── Try LLM first ──
        if llm_available():
            try:
                llm_result = llm_understand(text)
                if llm_result and llm_result.get("intent") != "unknown":
                    intent   = llm_result["intent"]
                    params   = llm_result.get("params", {})
                    response = llm_result.get("response", "Done.")
                    os_cmd   = llm_result.get("os_command")

                    # Security: Human-in-The-Loop
                    if os_cmd and intent not in INTENT_HANDLERS:
                        print(f"\n[SECURITY] Sypher generated a new command for '{intent}':\n  {os_cmd}")
                        ans = input("Do you want to allow this? (y/n): ").strip().lower()
                        if ans not in ("y", "yes"):
                            print("[SECURITY] Command denied.")
                            return {
                                "input":      text,
                                "intent":     intent,
                                "confidence": 1.0,
                                "response":   f"Command '{intent}' denied by user.",
                                "params":     params,
                                "engine":     "llm",
                            }
                        
                        save_dynamic_command(intent, os_cmd)

                    # Execute the OS command
                    actual = execute(intent, params=params)
                    
                    # Continuously learn from this command
                    if add_to_dataset(text, intent):
                        import threading
                        self._phrase_cnt += 1
                        print(f"[Assistant] Learning new phrase: '{text[:40]}...' ({self._phrase_cnt}/5)")
                        
                        if self._phrase_cnt >= 5:
                            self._phrase_cnt = 0
                            print("[Assistant] Batch retraining ML model in background...")
                            def _background_train():
                                try:
                                    new_model = train()
                                    self.model = new_model
                                    print("[Assistant] Background ML retrain complete.")
                                except Exception as e:
                                    print(f"[Assistant] Background train error: {e}")
                            threading.Thread(target=_background_train, daemon=True).start()

                    # For dynamic intents, prefer the executor's live data
                    if intent in ("get_time", "get_date", "get_battery",
                                  "get_ip_address"):
                        response = actual

                    return {
                        "input":      text,
                        "intent":     intent,
                        "confidence": 1.0,
                        "response":   response,
                        "params":     params,
                        "engine":     "llm",
                    }
            except Exception as e:
                print(f"[Assistant] LLM error: {e}")

        # ── Fallback: ML classifier ──
        intent, confidence = self.predict_intent(text)

        if confidence < CONFIDENCE_THRESHOLD:
            return {
                "input":      text,
                "intent":     "unknown",
                "confidence": round(confidence, 4),
                "response":   "I'm not sure what you meant. Could you please rephrase?",
                "params":     {},
                "engine":     "ml",
            }

        params   = extract_slots(intent, text)
        response = execute(intent, params=params)

        return {
            "input":      text,
            "intent":     intent,
            "confidence": round(confidence, 4),
            "response":   response,
            "params":     params,
            "engine":     "ml",
        }

    # ── Main loop (with wake-word detection) ─────────────────────
    def run(self, continuous: bool = True):
        self.running = True
        engine_str = "LLM (Gemini)" if llm_available() else "ML classifier"
        speak(f"Voice Assistant is ready using {engine_str}. "
              "Say 'Hey Assistant' to wake me up.")

        while self.running:
            text = listen()
            if text is None:
                continue

            text_lower = text.lower().strip()

            if any(q in text_lower for q in QUIT_WORDS):
                speak("Goodbye! Have a great day.")
                self.running = False
                break

            if not any(w in text_lower for w in WAKE_WORDS):
                continue

            speak("How can I help?")
            command_text = listen()

            if command_text is None:
                speak("I didn't catch that. Say my name again when ready.")
                continue

            if any(q in command_text.lower().strip() for q in QUIT_WORDS):
                speak("Goodbye! Have a great day.")
                self.running = False
                break

            result = self.process_command(command_text)
            print(f"[Assistant] [{result['engine'].upper()}] "
                  f"Intent: '{result['intent']}'  "
                  f"Params: {result['params']}")
            speak(result["response"])

            if not continuous:
                break


if __name__ == "__main__":
    assistant = VoiceAssistant()
    try:
        assistant.run(continuous=True)
    except KeyboardInterrupt:
        print("\n[Assistant] Interrupted by user.")
        speak("Shutting down. Goodbye!")
