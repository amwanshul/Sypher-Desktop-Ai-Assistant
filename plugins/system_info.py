"""
plugins/system_info.py
System information handlers (Time, Date, IP Address, Battery).
"""
import socket
import datetime
import subprocess
from . import register_intent
from .utils import OS

# These intents are dynamic, so they compute the response in the handler
# and we can map them back to strings easily. I will make the handlers return strings!
# Wait, command_executor.py expects them to return True, and then it generates the string
# in `_build_dynamic_response()`. To make plugins truly self-contained, these handlers
# should return the response string themselves if `is_dynamic`, or we can just 
# register them with a dynamic builder!
# Let's change the pattern: if a handler returns a string, that string is used as the response.

@register_intent("get_time", "Checking the time.", is_dynamic=True)
def get_time(**kw):
    return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}."

@register_intent("get_date", "Checking the date.", is_dynamic=True)
def get_date(**kw):
    return f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}."

@register_intent("get_battery", "Checking battery status.", is_dynamic=True)
def get_battery(**kw):
    try:
        import psutil
        battery = psutil.sensors_battery()
        if battery:
            plug = "plugged in" if battery.power_plugged else "on battery"
            return f"Battery is at {battery.percent:.0f}% ({plug})."
        return "Could not read battery info."
    except ImportError:
        if OS == "Windows":
            try:
                r = subprocess.run(["powershell", "-NoProfile", "-Command", "(Get-WmiObject Win32_Battery).EstimatedChargeRemaining"], capture_output=True, text=True, timeout=10)
                pct = r.stdout.strip()
                if pct.isdigit(): return f"Battery is at {pct}%."
            except Exception: pass
        return "Could not read battery (install psutil for best results)."

@register_intent("get_ip_address", "Checking your IP address.", is_dynamic=True)
def get_ip_address(**kw):
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return f"Your local IP address is {ip}."
    except Exception:
        return "Could not determine your IP address."
