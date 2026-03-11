"""
plugins/media.py
Media controls like Volume and Mute.
"""
import time
import subprocess
from . import register_intent
from .utils import OS

def _win_send_vk(code: int):
    subprocess.run(
        ["powershell", "-NoProfile", "-Command", f"$wsh = New-Object -ComObject WScript.Shell; $wsh.SendKeys([char]{code})"],
        capture_output=True, timeout=10
    )

@register_intent("volume_up", "Increasing the volume.")
def volume_up(**kw):
    if OS == "Windows":
        for _ in range(5):
            _win_send_vk(175)
            time.sleep(0.04)
    elif OS == "Darwin":
        subprocess.call(["osascript", "-e", "set volume output volume (output volume of (get volume settings) + 10)"])
    else:
        subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "10%+"])
    return True

@register_intent("volume_down", "Decreasing the volume.")
def volume_down(**kw):
    if OS == "Windows":
        for _ in range(5):
            _win_send_vk(174)
            time.sleep(0.04)
    elif OS == "Darwin":
        subprocess.call(["osascript", "-e", "set volume output volume (output volume of (get volume settings) - 10)"])
    else:
        subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "10%-"])
    return True

@register_intent("mute", "Toggling mute.")
def mute(**kw):
    if OS == "Windows":
        _win_send_vk(173)
    elif OS == "Darwin":
        subprocess.call(["osascript", "-e", "set volume output muted true"])
    else:
        subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "toggle"])
    return True
