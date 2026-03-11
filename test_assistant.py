"""
test_assistant.py  v6
Tests for the intent classifier, command dispatcher, slot extractor,
and unified process_command() pipeline.
Run with:  python test_assistant.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from model_trainer    import train, preprocess
from command_executor import INTENT_HANDLERS
from slot_extractor   import extract_slots, _resolve_user_folder


# ──────────────────────────────────────────────
# Test cases  (command text → expected intent)
# ──────────────────────────────────────────────
TEST_CASES = [
    # Original tests
    ("open chrome",           "open_browser"),
    ("launch browser",        "open_browser"),
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
    ("volume up",             "volume_up"),
    ("louder",                "volume_up"),
    ("volume down",           "volume_down"),
    ("quieter",               "volume_down"),
    ("mute sound",            "mute"),
    ("take screenshot",       "take_screenshot"),
    ("hello",                 "greet"),
    ("how are you",           "greet"),

    # New: search_web (parameterised)
    ("search for leetcode",                   "search_web"),
    ("google machine learning",               "search_web"),
    ("open browser and search for weather",   "search_web"),
    ("search for python tutorials",           "search_web"),

    # New: search_youtube (parameterised)
    ("open youtube and search for cats",      "search_youtube"),
    ("search youtube for music",              "search_youtube"),
    ("youtube search for recipes",            "search_youtube"),

    # New: system/internal
    ("what time is it",       "get_time"),
    ("current time",          "get_time"),
    ("what day is it",        "get_date"),
    ("battery level",         "get_battery"),
    ("what is my ip",         "get_ip_address"),
    ("open settings",         "open_settings"),
    ("lock screen",           "lock_screen"),
    ("empty recycle bin",     "empty_recycle_bin"),
    ("open terminal",         "open_cmd"),
    ("open command prompt",   "open_cmd"),

    # New: open_folder_path
    ("open folder documents",  "open_folder_path"),
    ("open my pictures",       "open_folder_path"),
]


# ──────────────────────────────────────────────
# Slot extraction tests (uses _resolve_user_folder
# to dynamically determine expected path)
# ──────────────────────────────────────────────
SLOT_TESTS = [
    ("search_web",    "search for leetcode",                   {"query": "leetcode"}),
    ("search_web",    "google machine learning",               {"query": "machine learning"}),
    ("search_web",    "open browser and search for weather",   {"query": "weather"}),
    ("search_youtube","open youtube and search for cats",      {"query": "cats"}),
    ("search_youtube","search youtube for coding tutorials",   {"query": "coding tutorials"}),
    ("open_folder_path", "open folder documents",
        {"path": _resolve_user_folder("Documents"),
         "folder_name": "Documents"}),
    ("close_app",     "close chrome",                          {"app_name": "chrome"}),
    ("close_app",     "close app",                             {}),
    ("greet",         "hello",                                 {}),
]


def run_tests(model):
    passed = 0
    failed = 0
    print("\n" + "="*70)
    print(f"{'INTENT CLASSIFICATION TESTS':^70}")
    print("="*70)
    print(f"{'Command':<40} {'Expected':<20} {'Got':<20} {'Conf':>6}")
    print("-"*70)

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
        print(f"{status} {command:<39} {expected_intent:<20} {predicted:<20} {conf:6.2%}")

    print("="*70)
    total = passed + failed
    print(f"Results: {passed}/{total} passed  ({passed/total:.0%})")
    print("="*70)
    return passed, failed


def test_slot_extraction():
    print("\n" + "="*70)
    print(f"{'SLOT EXTRACTION TESTS':^70}")
    print("="*70)
    passed = 0
    failed = 0

    for intent, raw_text, expected_slots in SLOT_TESTS:
        result = extract_slots(intent, raw_text)
        ok = result == expected_slots
        status = "✓" if ok else "✗"
        if ok:
            passed += 1
        else:
            failed += 1
        print(f"{status} ({intent}) '{raw_text}'")
        if not ok:
            print(f"    Expected: {expected_slots}")
            print(f"    Got:      {result}")

    print("-"*70)
    total = passed + failed
    print(f"Slot Results: {passed}/{total} passed  ({passed/total:.0%})")
    print("="*70)
    return passed, failed


def test_preprocessor():
    print("\n[Preprocessor Tests]")
    cases = [
        ("Open CHROME!",   "open chrome"),
        ("Shut Down the Computer.", "shut down computer"),
        ("Volume UP",      "volume up"),
    ]
    ok = True
    for raw, expected in cases:
        result = preprocess(raw)
        status = "✓" if result == expected else "✗"
        if result != expected:
            ok = False
        print(f"  {status} '{raw}' → '{result}' (expected: '{expected}')")
    return ok


def test_handlers_registered():
    print("\n[Handler Registration Check]")
    expected_intents = [
        "open_browser", "open_calculator", "open_file_explorer",
        "open_notepad", "open_task_manager", "close_app",
        "shutdown", "restart", "volume_up", "volume_down",
        "mute", "take_screenshot", "greet",
        # New intents
        "search_google", "search_web", "search_youtube",
        "open_youtube", "open_gmail",
        "open_downloads", "open_desktop", "create_folder", "open_folder_path",
        "open_spotify", "open_whatsapp", "open_vscode",
        "open_excel", "open_word", "open_powerpoint",
        "get_time", "get_date", "get_battery", "get_ip_address",
        "open_settings", "lock_screen", "empty_recycle_bin", "open_cmd",
    ]
    all_ok = True
    for intent in expected_intents:
        status = "✓" if intent in INTENT_HANDLERS else "✗  MISSING"
        if intent not in INTENT_HANDLERS:
            all_ok = False
        print(f"  {status}  {intent}")
    return all_ok


def test_no_os_system():
    """Verify that command_executor.py contains no os.system() calls."""
    print("\n[Security: No os.system() Check]")
    executor_path = os.path.join(os.path.dirname(__file__),
                                  "command_executor.py")
    with open(executor_path, "r") as f:
        content = f.read()
    count = content.count("os.system(")
    if count == 0:
        print("  ✓  No os.system() calls found — injection-safe")
        return True
    else:
        print(f"  ✗  Found {count} os.system() call(s) — needs remediation")
        return False


if __name__ == "__main__":
    print("Training model for tests …")
    model = train()

    preproc_ok     = test_preprocessor()
    handlers_ok    = test_handlers_registered()
    security_ok    = test_no_os_system()
    cls_passed, cls_failed = run_tests(model)
    slot_passed, slot_failed = test_slot_extraction()

    total_failed = (cls_failed + slot_failed
                    + (0 if handlers_ok else 1)
                    + (0 if preproc_ok else 1)
                    + (0 if security_ok else 1))
    sys.exit(0 if total_failed == 0 else 1)
