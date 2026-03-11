"""
dataset.py
Loads the ML command dataset from a robust external JSON database.
Provides safety, modularity, and easy extension.
"""

import os
import json

_JSON_DB_PATH = os.path.join(os.path.dirname(__file__), "dataset.json")

def load_dataset() -> list:
    """Load the dataset from the JSON file on disk."""
    if not os.path.exists(_JSON_DB_PATH):
        print("[Dataset] Warning: dataset.json not found!")
        return []
        
    try:
        with open(_JSON_DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            # The JSON array contains sub-arrays: [["open browser", "open_browser"], ...]
            return [tuple(row) for row in data]
    except Exception as e:
        print(f"[Dataset] Failed to load dataset: {e}")
        return []

# Expose as a global list matching the previous API architecture
COMMAND_DATASET = load_dataset()

def add_to_dataset(text: str, intent: str) -> bool:
    """
    Appends a new (command, intent) pair to dataset.json safely.
    Returns True if successfully added.
    """
    text = text.lower().strip()
    
    # Check if already exists in memory
    for existing_text, _ in COMMAND_DATASET:
        if existing_text == text:
            return False
            
    # Always append to memory list immediately
    tup = (text, intent)
    COMMAND_DATASET.append(tup)
    
    # Save permanently to JSON disk file
    try:
        data = [[t, i] for t, i in COMMAND_DATASET]
        with open(_JSON_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"[Dataset] Learned new command: '{text}' → '{intent}'")
        return True
    except Exception as e:
        print(f"[Dataset] Failed to save new command to database: {e}")
        
    return False