"""
plugins/utils.py
Shared helper functions for all executor plugins.
"""
import os
import platform
import subprocess

OS = platform.system()   # "Windows" | "Darwin" | "Linux"

def open_url(url: str) -> bool:
    """Open a URL in the system default browser."""
    try:
        if OS == "Windows":
            subprocess.Popen(["cmd", "/c", "start", "", url])
        elif OS == "Darwin":
            subprocess.Popen(["open", url])
        else:
            subprocess.Popen(["xdg-open", url])
        return True
    except Exception as e:
        print(f"[Executor] open_url error: {e}")
        return False

def open_folder(path: str) -> bool:
    """Open a folder in the system file manager."""
    try:
        os.makedirs(path, exist_ok=True)   # create if missing
        if OS == "Windows":
            subprocess.Popen(["explorer", path])
        elif OS == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return True
    except Exception as e:
        print(f"[Executor] open_folder error: {e}")
        return False

def launch(exe_path: str) -> bool:
    """Launch an executable by full path."""
    try:
        subprocess.Popen([exe_path])
        return True
    except Exception as e:
        print(f"[Executor] launch error: {e}")
        return False
