"""
slot_extractor.py
─────────────────────────────────────────────────────────────────
Extracts parameters (slots) from the raw user text based on
the predicted intent.

Returns a dict of   param_name → value   (empty dict if nothing
to extract for that intent).
"""

import re
import os


# ── Known user folders (mapped to ~ paths) ────────────────────
_KNOWN_FOLDERS = {
    "documents":  "Documents",
    "document":   "Documents",
    "docs":       "Documents",
    "pictures":   "Pictures",
    "picture":    "Pictures",
    "photos":     "Pictures",
    "photo":      "Pictures",
    "music":      "Music",
    "videos":     "Videos",
    "video":      "Videos",
    "downloads":  "Downloads",
    "download":   "Downloads",
    "desktop":    "Desktop",
}

# ── Patterns to strip from the front of a query ──────────────
_SEARCH_WEB_PREFIXES = [
    r"open\s+browser\s+and\s+search\s+for\s+",
    r"browser\s+search\s+for\s+",
    r"search\s+the\s+web\s+for\s+",
    r"search\s+online\s+for\s+",
    r"web\s+search\s+for\s+",
    r"search\s+for\s+",
    r"look\s+up\s+",
    r"find\s+information\s+about\s+",
    r"google\s+",
]

_SEARCH_YT_PREFIXES = [
    r"open\s+youtube\s+and\s+search\s+for\s+",
    r"search\s+youtube\s+for\s+",
    r"youtube\s+search\s+for\s+",
    r"search\s+on\s+youtube\s+for\s+",
    r"find\s+on\s+youtube\s+",
    r"look\s+up\s+on\s+youtube\s+",
    r"play\s+on\s+youtube\s+",
    r"youtube\s+find\s+",
    r"search\s+videos\s+for\s+",
    r"find\s+videos\s+about\s+",
    r"look\s+for\s+videos\s+about\s+",
]

_FOLDER_PREFIXES = [
    r"open\s+folder\s+",
    r"go\s+to\s+(?:my\s+)?",
    r"navigate\s+to\s+(?:my\s+)?",
    r"open\s+my\s+",
    r"browse\s+(?:my\s+)?",
    r"show\s+me\s+my\s+",
]

_CLOSE_PREFIXES = [
    r"close\s+",
    r"exit\s+",
    r"quit\s+",
    r"terminate\s+",
    r"kill\s+",
]


def extract_slots(intent: str, raw_text: str) -> dict:
    """
    Given a predicted intent and the raw (original) user text,
    extract any parameters required by the handler.

    Returns:
        dict  – e.g. {"query": "leetcode"}, {"path": "Documents"},
                or {} if no slots needed.
    """
    text = raw_text.strip()

    if intent == "search_web":
        return _extract_search_query(text, _SEARCH_WEB_PREFIXES)

    if intent == "search_youtube":
        return _extract_search_query(text, _SEARCH_YT_PREFIXES)

    if intent == "open_folder_path":
        return _extract_folder_path(text)

    if intent == "close_app":
        return _extract_app_name(text)

    return {}


# ─────────────────────────────────────────────────────────────
# Private helpers
# ─────────────────────────────────────────────────────────────

def _extract_search_query(text: str, prefixes: list) -> dict:
    """Strip known prefix patterns and return the remainder as query."""
    lower = text.lower()
    for pat in prefixes:
        m = re.match(pat, lower)
        if m:
            query = text[m.end():].strip()
            if query:
                return {"query": query}
    # Fallback: everything after first "for" / "about"
    for kw in ["for ", "about "]:
        idx = lower.find(kw)
        if idx != -1:
            q = text[idx + len(kw):].strip()
            if q:
                return {"query": q}
    return {}


def _extract_folder_path(text: str) -> dict:
    """Extract a known folder name from the text."""
    lower = text.lower()
    # Try to strip prefixes first
    remainder = lower
    for pat in _FOLDER_PREFIXES:
        m = re.match(pat, lower)
        if m:
            remainder = lower[m.end():].strip()
            break
    # Remove trailing "folder"
    remainder = re.sub(r"\s+folder$", "", remainder).strip()
    # Match against known folders
    if remainder in _KNOWN_FOLDERS:
        folder = _KNOWN_FOLDERS[remainder]
        full_path = os.path.join(os.path.expanduser("~"), folder)
        return {"path": full_path, "folder_name": folder}
    # Try to find any known folder word anywhere in text
    for keyword, folder in _KNOWN_FOLDERS.items():
        if keyword in lower.split():
            full_path = os.path.join(os.path.expanduser("~"), folder)
            return {"path": full_path, "folder_name": folder}
    return {}


def _extract_app_name(text: str) -> dict:
    """Extract the app name from a close command."""
    lower = text.lower()
    for pat in _CLOSE_PREFIXES:
        m = re.match(pat, lower)
        if m:
            app = text[m.end():].strip()
            if app and app not in ("app", "application", "the app"):
                return {"app_name": app}
    return {}
