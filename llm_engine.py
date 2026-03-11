"""
llm_engine.py
─────────────────────────────────────────────────────────────────
Gemini-powered command understanding.

Replaces the TF-IDF + Logistic Regression classifier with the
Gemini Flash API. Given raw user text, returns a structured dict
with intent, params, and a natural-language response.

Falls back gracefully when the API is unreachable.
─────────────────────────────────────────────────────────────────
"""

import os
import json
import re
import sys

# ── Load API key from .env ────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass  # dotenv not installed; key must be in environment

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# ── Gemini SDK ────────────────────────────────────────────────
_model = None

def _get_model():
    """Lazy-init the Gemini model."""
    global _model
    if _model is not None:
        return _model
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        _model = genai.GenerativeModel(
            "gemini-2.0-flash",
            generation_config={
                "temperature": 0.1,
                "max_output_tokens": 300,
            },
        )
        return _model
    except Exception as e:
        print(f"[LLM] Failed to init Gemini: {e}")
        return None


# ── System prompt ─────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are the command parser for a desktop voice assistant called Sypher.
Your job is to understand the user's spoken command and return a JSON object.

## Supported intents and their params:

| intent             | params                | description                       |
|--------------------|-----------------------|-----------------------------------|
| open_browser       | —                     | Open default web browser          |
| open_calculator    | —                     | Open calculator app               |
| open_file_explorer | —                     | Open file explorer                |
| open_notepad       | —                     | Open text editor                  |
| open_task_manager  | —                     | Open task manager                 |
| close_app          | app_name (optional)   | Close an app by name              |
| shutdown           | —                     | Shutdown the computer             |
| restart            | —                     | Restart the computer              |
| volume_up          | —                     | Increase volume                   |
| volume_down        | —                     | Decrease volume                   |
| mute               | —                     | Toggle mute                       |
| take_screenshot    | —                     | Capture screen                    |
| greet              | —                     | User greeting                     |
| search_google      | —                     | Open Google homepage              |
| search_web         | query (required)      | Search Google for a query         |
| search_youtube     | query (required)      | Search YouTube for a query        |
| open_youtube       | —                     | Open YouTube homepage             |
| open_gmail         | —                     | Open Gmail                        |
| open_downloads     | —                     | Open Downloads folder             |
| open_desktop       | —                     | Open Desktop folder               |
| create_folder      | —                     | Create new folder on Desktop      |
| open_folder_path   | folder_name (required)| Open a named folder (Documents, Pictures, etc.) |
| open_spotify       | —                     | Open Spotify                      |
| open_whatsapp      | —                     | Open WhatsApp                     |
| open_vscode        | —                     | Open VS Code                      |
| open_excel         | —                     | Open Excel                        |
| open_word          | —                     | Open Word                         |
| open_powerpoint    | —                     | Open PowerPoint                   |
| get_time           | —                     | Tell current time                 |
| get_date           | —                     | Tell today's date                 |
| get_battery        | —                     | Check battery level               |
| get_ip_address     | —                     | Show local IP address             |
| open_settings      | —                     | Open system settings              |
| lock_screen        | —                     | Lock the computer                 |
| empty_recycle_bin  | —                     | Empty Recycle Bin / Trash         |
| open_cmd           | —                     | Open terminal / command prompt    |

## Rules for Zero-Shot Commands:
If the user asks for a command NOT found in the table above (e.g., "open camera"):
1. Invent a short, snake_case intent name (e.g., "open_camera").
2. Your JSON MUST include an "os_command" key containing the exact, safe terminal command to execute it on {OS}.
3. The os_command should be a string ready for subprocess.Popen(..., shell=True). E.g., for Windows camera: "start microsoft.windows.camera:"

## General Rules:
1. Return ONLY valid JSON — no markdown, no explanation, no extra text.
2. The JSON must have exactly these keys: "intent", "params", "response" (plus "os_command" if zero-shot).
3. "params" must be a JSON object (empty {} if no params needed).
4. "response" is a short, friendly confirmation message (1 sentence).

## Examples:
User: "open browser and search for leetcode"
{"intent": "search_web", "params": {"query": "leetcode"}, "response": "Searching the web for leetcode."}

User: "what time is it"
{"intent": "get_time", "params": {}, "response": "Let me check the time for you."}

User: "open camera"
{"intent": "open_camera", "params": {}, "response": "Opening the camera.", "os_command": "start microsoft.windows.camera:"}
"""

# ── Public API ────────────────────────────────────────────────

def llm_available() -> bool:
    """Check if the LLM engine is usable (API key set + SDK importable)."""
    if not GEMINI_API_KEY:
        return False
    try:
        import google.generativeai  # noqa: F401
        return True
    except ImportError:
        return False


def llm_understand(text: str) -> dict | None:
    """
    Send user text to Gemini and return a structured result dict,
    or None if the API call fails for any reason.

    Returns:
        {
            "intent":     str,       # e.g. "search_web"
            "params":     dict,      # e.g. {"query": "leetcode"}
            "response":   str,       # e.g. "Searching the web for leetcode."
            "os_command": str|None,  # Only if zero-shot
            "engine":     "llm",     # always "llm"
        }
        or None on failure.
    """
    model = _get_model()
    if model is None:
        return None

    import platform
    current_os = platform.system() # "Windows" | "Darwin" | "Linux"
    prompt = _SYSTEM_PROMPT.replace("{OS}", current_os)

    try:
        chat = model.start_chat(history=[])
        result = chat.send_message(
            f"{prompt}\n\nUser command: \"{text}\""
        )
        raw = result.text.strip()

        # Strip markdown code fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        parsed = json.loads(raw)

        # Validate structure
        intent     = parsed.get("intent", "unknown")
        params     = parsed.get("params", {})
        response   = parsed.get("response", "Done.")
        os_cmd     = parsed.get("os_command", None)

        if not isinstance(params, dict):
            params = {}

        return {
            "intent":     intent,
            "params":     params,
            "response":   response,
            "os_command": os_cmd,
            "engine":     "llm",
        }

    except json.JSONDecodeError as e:
        print(f"[LLM] JSON parse error: {e}")
        print(f"[LLM] Raw response: {raw[:200]}")
        return None
    except Exception as e:
        print(f"[LLM] API error: {e}")
        return None
