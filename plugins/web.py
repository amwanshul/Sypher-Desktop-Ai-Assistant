"""
plugins/web.py
Handles web browsing and search intents.
"""
from urllib.parse import quote_plus
from . import register_intent
from .utils import open_url

@register_intent("open_browser", "Opening your browser.")
def open_browser(**kw):
    return open_url("https://www.google.com")

@register_intent("search_google", "Opening Google.")
def search_google(**kw):
    return open_url("https://www.google.com")

@register_intent("search_web", "Searching the web.", is_parameterised=True, is_dynamic=True)
def search_web(params=None, **kw):
    """Open Google search with an extracted query."""
    query = (params or {}).get("query", "")
    if query:
        url = f"https://www.google.com/search?q={quote_plus(query)}"
        open_url(url)
        return f"Searching the web for '{query}'."
    open_url("https://www.google.com")
    return "Opening Google."

@register_intent("search_youtube", "Searching YouTube.", is_parameterised=True, is_dynamic=True)
def search_youtube(params=None, **kw):
    """Open YouTube search with an extracted query."""
    query = (params or {}).get("query", "")
    if query:
        url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
        open_url(url)
        return f"Searching YouTube for '{query}'."
    open_url("https://www.youtube.com")
    return "Opening YouTube."

@register_intent("open_youtube", "Opening YouTube.")
def open_youtube(**kw):
    return open_url("https://www.youtube.com")

@register_intent("open_gmail", "Opening Gmail.")
def open_gmail(**kw):
    return open_url("https://mail.google.com")
