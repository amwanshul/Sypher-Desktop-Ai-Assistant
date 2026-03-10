"""
test_assistant.py
Tests for the intent classifier and command dispatcher.
Run with:  python test_assistant.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from model_trainer    import train, preprocess
from command_executor import INTENT_HANDLERS


# ──────────────────────────────────────────────
# Test cases  (command text → expected intent)
# ──────────────────────────────────────────────
TEST_CASES = [
    ("open chrome",           "open_browser"),
    ("launch browser",        "open_browser"),
    ("start firefox",         "open_browser"),
    ("open calculator",       "open_calculator"),
    ("start calc",            "open_calculator"),
    ("open file explorer",    "open_file_explorer"),
    ("show files",            "open_file_explorer"),
    ("open notepad",          "open_notepad"),
    ("open task manager",     "open_task_manager"),
    ("close chrome",          "close_app"),
    ("shutdown system",       "shutdown"),
    ("turn off computer",     "shutdown"),
    ("restart system",        "restart"),
    ("reboot",                "restart"),
    ("volume up",             "volume_up"),
    ("louder",                "volume_up"),
    ("volume down",           "volume_down"),
    ("quieter",               "volume_down"),
    ("mute sound",            "mute"),
    ("take screenshot",       "take_screenshot"),
    ("hello",                 "greet"),
    ("how are you",           "greet"),
]


def run_tests(model):
    passed = 0
    failed = 0
    print("\n" + "="*60)
    print(f"{'TEST SUITE':^60}")
    print("="*60)
    print(f"{'Command':<35} {'Expected':<20} {'Got':<20} {'Conf':>6}")
    print("-"*60)

    for command, expected_intent in TEST_CASES:
        processed = preprocess(command)
        proba     = model.predict_proba([processed])[0]
        classes   = model.classes_
        idx       = proba.argmax()
        predicted = classes[idx]
        conf      = proba[idx]
        ok        = predicted == expected_intent
        status    = "✓" if ok else "✗"
        if ok:
            passed += 1
        else:
            failed += 1
        print(f"{status} {command:<34} {expected_intent:<20} {predicted:<20} {conf:6.2%}")

    print("="*60)
    total = passed + failed
    print(f"Results: {passed}/{total} passed  ({passed/total:.0%})")
    print("="*60)
    return passed, failed


def test_preprocessor():
    print("\n[Preprocessor Tests]")
    cases = [
        ("Open CHROME!",   "open chrome"),
        ("Shut Down the Computer.", "shut computer"),  # stopwords removed
    ]
    for raw, _ in cases:
        result = preprocess(raw)
        print(f"  '{raw}' → '{result}'")


def test_handlers_registered():
    print("\n[Handler Registration Check]")
    expected_intents = [
        "open_browser", "open_calculator", "open_file_explorer",
        "open_notepad", "open_task_manager", "close_app",
        "shutdown", "restart", "volume_up", "volume_down",
        "mute", "take_screenshot", "greet",
    ]
    for intent in expected_intents:
        status = "✓" if intent in INTENT_HANDLERS else "✗  MISSING"
        print(f"  {status}  {intent}")


if __name__ == "__main__":
    print("Training model for tests …")
    model = train()

    test_preprocessor()
    test_handlers_registered()
    passed, failed = run_tests(model)

    sys.exit(0 if failed == 0 else 1)
