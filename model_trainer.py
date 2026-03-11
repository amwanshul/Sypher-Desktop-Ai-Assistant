"""
model_trainer.py
Trains TF-IDF + Logistic Regression classifier and saves it to disk.
"""

import os
import re
import pickle
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
import numpy as np

from dataset import COMMAND_DATASET

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

# Common English stopwords (built-in, no NLTK needed).
# Action-critical words (up, down, on, off, all) are intentionally
# excluded so they pass through to TF-IDF as meaningful features.
_STOPWORDS = {
    "a","an","the","is","it","in","at","to","for","of","and","or","but",
    "i","my","me","we","you","he","she","they","this","that","these","those",
    "be","are","was","were","have","has","had","do","does","did","will","would",
    "can","could","should","may","might","shall","am","been","being",
    "with","from","by","as","into","through","during","before","after",
    "please","just","now","then","so","if","about","out","there","here",
}


# ──────────────────────────────────────────────
# Text Preprocessing
# ──────────────────────────────────────────────
def preprocess(text: str) -> str:
    """Lowercase → remove punctuation → tokenize → remove stopwords → rejoin."""
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    tokens = text.split()
    tokens = [t for t in tokens if t not in _STOPWORDS]
    return " ".join(tokens)


# ──────────────────────────────────────────────
# Training
# ──────────────────────────────────────────────
def train():
    texts, labels = zip(*COMMAND_DATASET)
    processed = [preprocess(t) for t in texts]

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=500)),
        ("clf",   LogisticRegression(max_iter=1000, C=5.0, solver="lbfgs",
                                     random_state=42)),
    ])

    # Cross-validation accuracy
    scores = cross_val_score(pipeline, processed, labels, cv=5, scoring="accuracy")
    print(f"[Trainer] Cross-validation accuracy: {np.mean(scores):.2%} ± {np.std(scores):.2%}")

    # Train on full dataset
    pipeline.fit(processed, labels)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(pipeline, f)
    print(f"[Trainer] Model saved → {MODEL_PATH}")
    return pipeline


def load_model():
    if not os.path.exists(MODEL_PATH):
        print("[Trainer] No saved model found – training now …")
        return train()
    with open(MODEL_PATH, "rb") as f:
        pipeline = pickle.load(f)
    print("[Trainer] Model loaded from disk.")
    return pipeline


if __name__ == "__main__":
    train()
