"""
plugins/__init__.py
Dynamic Plugin Manager.
Plugins register their intents here so that command_executor.py can dynamically call them.
"""

import importlib
import pkgutil

INTENT_HANDLERS = {}
PARAMETERISED_INTENTS = set()
DYNAMIC_INTENTS = set()

def register_intent(intent: str, default_response: str, is_parameterised: bool = False, is_dynamic: bool = False):
    """
    Decorator for registering an intent handler.
    Example:
        @register_intent("open_browser", "Opening your browser.")
        def open_browser(**kw):
            ...
    """
    def decorator(func):
        INTENT_HANDLERS[intent] = (func, default_response)
        if is_parameterised:
            PARAMETERISED_INTENTS.add(intent)
        if is_dynamic:
            DYNAMIC_INTENTS.add(intent)
        return func
    return decorator

def load_plugins():
    """Import all python modules in the plugins/ directory to register them."""
    package_name = __name__
    for _, module_name, _ in pkgutil.iter_modules(__path__):
        importlib.import_module(f"{package_name}.{module_name}")
