# AI-Based Voice Controlled Desktop Automation Assistant

A lightweight, **fully local** desktop voice assistant that understands spoken commands
and controls your computer — no cloud required.

---

## Features

| Intent              | Example commands                                   |
|---------------------|----------------------------------------------------|
| Open browser        | "Open Chrome", "Launch browser"                    |
| Open calculator     | "Open calculator", "Start calc"                    |
| Open file explorer  | "Open file explorer", "Show my files"              |
| Open Notepad        | "Open Notepad", "Open text editor"                 |
| Open Task Manager   | "Open Task Manager", "Show running processes"      |
| Close app           | "Close Chrome", "Exit application"                 |
| Shutdown            | "Shutdown system", "Turn off computer"             |
| Restart             | "Restart system", "Reboot"                         |
| Volume up           | "Volume up", "Louder"                              |
| Volume down         | "Volume down", "Quieter"                           |
| Mute                | "Mute", "Silence"                                  |
| Take screenshot     | "Take screenshot", "Capture screen"                |
| Greet               | "Hello", "How are you", "What can you do"          |

---

## Project Structure

```
ai_voice_assistant/
├── assistant.py          # Main orchestrator & entry point
├── dataset.py            # Labelled command dataset (100+ examples)
├── model_trainer.py      # TF-IDF + Logistic Regression pipeline
├── command_executor.py   # OS-level command dispatcher
├── voice_io.py           # Microphone input & TTS output
├── test_assistant.py     # Automated test suite
├── requirements.txt      # Python dependencies
└── README.md
```

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

> **PyAudio note (Windows):** If `pip install pyaudio` fails, download the
> matching wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
> and install it with `pip install <wheel_file>.whl`

> **PyAudio note (Linux):**
> ```bash
> sudo apt-get install portaudio19-dev python3-pyaudio
> ```

> **PyAudio note (macOS):**
> ```bash
> brew install portaudio && pip install pyaudio
> ```

### 2. Train the Model

```bash
python model_trainer.py
```

This trains the TF-IDF + Logistic Regression classifier and saves `model.pkl`.

### 3. Run the Assistant

```bash
python assistant.py
```

Say a command into your microphone (or type it when prompted).
Say **"quit"** or **"goodbye"** to exit.

### 4. Run Tests

```bash
python test_assistant.py
```

---

## Architecture

```
Microphone
    │
    ▼
Voice Input (SpeechRecognition / keyboard fallback)
    │
    ▼
Text Preprocessing  (lowercase → punctuation removal → tokenize → stopword removal)
    │
    ▼
TF-IDF Vectorization  (unigrams + bigrams, 500 features)
    │
    ▼
Logistic Regression Classifier
    │
    ▼
Intent Prediction  (with confidence score)
    │
    ▼
Command Executor  (subprocess / os – cross-platform)
    │
    ▼
Voice Feedback  (pyttsx3 TTS)
```

---

## Extending the Assistant

1. **Add a new command** – add labelled examples to `dataset.py`
2. **Add a handler** – implement a function in `command_executor.py` and register it in `INTENT_HANDLERS`
3. **Re-train** – run `python model_trainer.py`

---

## References

* Salton & Buckley (1988) – TF-IDF Text Representation  
* Pedregosa et al. (2011) – Scikit-learn Machine Learning Library  
* Jurafsky & Martin (2009) – Speech and Language Processing  
