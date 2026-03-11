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
import platform


# ─────────────────────────────────────────────────────────────
# Windows shell-folder resolution via environment / registry
# ─────────────────────────────────────────────────────────────

def _resolve_user_folder(canonical_name: str) -> str:
    """
    Resolve a canonical folder name (e.g. 'Documents', 'Pictures')
    to the actual path on the current OS, using environment variables
    and registry lookups for non-English localisations.

    Falls back to ~/canonical_name if nothing better is found.
    """
    # ── Windows: try the Shell Folders registry key ──
    if platform.system() == "Windows":
        # Map canonical names to Shell Folder registry value names
        _SHELL_FOLDER_MAP = {
            "Documents": "Personal",
            "Pictures":  "{0DDD015D-B06C-45D5-8C4C-F59713854639}",
            "Music":     "My Music",
            "Videos":    "My Video",
            "Downloads": "{374DE290-123F-4565-9164-39C4925E467B}",
            "Desktop":   "Desktop",
        }
        reg_value = _SHELL_FOLDER_MAP.get(canonical_name)
        if reg_value:
            try:
                import winreg
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion"
                    r"\Explorer\User Shell Folders"
                )
                path, _ = winreg.QueryValueEx(key, reg_value)
                winreg.CloseKey(key)
                # Expand %USERPROFILE% and similar env vars
                path = os.path.expandvars(path)
                if os.path.isdir(path):
                    return path
            except (ImportError, FileNotFoundError, OSError):
                pass

        # Fallback: USERPROFILE (still locale-independent)
        profile = os.environ.get("USERPROFILE", os.path.expanduser("~"))
        candidate = os.path.join(profile, canonical_name)
        if os.path.isdir(candidate):
            return candidate

    # ── macOS / Linux: XDG or simple ~ expansion ──
    if platform.system() != "Windows":
        # Try XDG user dirs on Linux
        xdg_map = {
            "Documents": "XDG_DOCUMENTS_DIR",
            "Pictures":  "XDG_PICTURES_DIR",
            "Music":     "XDG_MUSIC_DIR",
            "Videos":    "XDG_VIDEOS_DIR",
            "Downloads": "XDG_DOWNLOAD_DIR",
            "Desktop":   "XDG_DESKTOP_DIR",
        }
        xdg_var = xdg_map.get(canonical_name)
        if xdg_var:
            xdg_val = os.environ.get(xdg_var)
            if xdg_val and os.path.isdir(xdg_val):
                return xdg_val

    # ── Final fallback ──
    return os.path.join(os.path.expanduser("~"), canonical_name)


# ── Known user folders (keyword → canonical name) ─────────────
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
        dict  – e.g. {"query": "leetcode"}, {"path": "C:\\...\\Documents"},
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
    """Extract a known folder name and resolve to actual OS path."""
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
        full_path = _resolve_user_folder(folder)
        return {"path": full_path, "folder_name": folder}
    # Try to find any known folder word anywhere in text
    for keyword, folder in _KNOWN_FOLDERS.items():
        if keyword in lower.split():
            full_path = _resolve_user_folder(folder)
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
