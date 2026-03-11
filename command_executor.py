"""
command_executor.py
Dynamic plugin dispatcher and zero-shot command executor.
"""
import os
import json
import subprocess
from plugins import load_plugins, INTENT_HANDLERS

# Dynamically load and register all plugins
load_plugins()

_DYNAMIC_DB_PATH = os.path.join(os.path.dirname(__file__), "dynamic_commands.json")

def get_dynamic_commands() -> dict:
    """Load synthesised zero-shot commands from disk."""
    if not os.path.exists(_DYNAMIC_DB_PATH):
        return {}
    try:
        with open(_DYNAMIC_DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Executor] Failed to load dynamic database: {e}")
        return {}

def save_dynamic_command(intent: str, os_command: str):
    """Persist a newly learned LLM zero-shot capability to disk."""
    cmds = get_dynamic_commands()
    cmds[intent] = os_command
    try:
        with open(_DYNAMIC_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(cmds, f, indent=4)
        print(f"[Executor] Saved new dynamic command -> {intent}: {os_command}")
    except Exception as e:
        print(f"[Executor] Failed to save dynamic command: {e}")

def execute(intent: str, params: dict = None) -> str:
    """
    Dispatch an intent to its plugin handler and return a response string.
    If the intent is a known zero-shot dynamic command, run it natively.
    """
    # 1. Plugin Execution
    if intent in INTENT_HANDLERS:
        handler, default_response = INTENT_HANDLERS[intent]
        
        try:
            # We blindly pass params, the handler accepts kwargs
            result = handler(params=params)
            
            if not result:
                return f"Sorry, I could not complete '{intent}'."
                
            # If the handler returned a specific string response
            if isinstance(result, str):
                return result
                
            # If the handler just returned True, use the default string
            return default_response
            
        except Exception as e:
            print(f"[Executor] Plugin error for {intent}: {e}")
            return f"Error executing '{intent}'."

    # 2. Dynamic Zero-Shot Execution
    dyn_cmds = get_dynamic_commands()
    if intent in dyn_cmds:
        os_cmd = dyn_cmds[intent]
        try:
            subprocess.Popen(os_cmd, shell=True)
            return f"Executing {intent.replace('_', ' ')}."
        except Exception as e:
            return f"Failed to execute dynamic command: {e}"

    return f"I don't know how to handle '{intent}' yet."