# AI-Based Voice Controlled Desktop Automation Assistant

A lightweight **hybrid** desktop voice assistant that understands spoken commands
and controls your computer.

> [!NOTE]
> **Hybrid architecture**: High-accuracy speech recognition uses the
> Google Web Speech API (requires internet). When the cloud API is
> unreachable, the assistant falls back to PocketSphinx for offline
> recognition (lower accuracy). All NLP classification, slot extraction,
> and command execution run fully locally.

---

## Features

| Intent              | Example commands                                   |
|---------------------|-----------------------------------------------------|
| Open browser        | "Open Chrome", "Launch browser"                     |
| Open calculator     | "Open calculator", "Start calc"                     |
| Open file explorer  | "Open file explorer", "Show my files"               |
| Open Notepad        | "Open Notepad", "Open text editor"                  |
| Open Task Manager   | "Open Task Manager", "Show running processes"       |
| Close app           | "Close Chrome", "Exit application"                  |
| Shutdown            | "Shutdown system", "Turn off computer"              |
| Restart             | "Restart system", "Reboot"                          |
| Volume up / down    | "Volume up", "Louder", "Volume down", "Quieter"     |
| Mute                | "Mute", "Silence"                                   |
| Screenshot          | "Take screenshot", "Capture screen"                 |
| Greet               | "Hello", "How are you", "What can you do"           |
| **Search web**      | "Search for leetcode", "Google python tutorials"    |
| **Search YouTube**  | "Open YouTube and search for cats"                  |
| **Get time / date** | "What time is it", "What's today's date"            |
| **Battery status**  | "Battery level", "Check battery"                    |
| **IP address**      | "What's my IP"                                      |
| **Open settings**   | "Open settings", "System preferences"               |
| **Lock screen**     | "Lock screen", "Lock my PC"                         |
| **Recycle Bin**     | "Empty recycle bin", "Clear trash"                  |
| **Open terminal**   | "Open terminal", "Open command prompt"              |
| **Open folder**     | "Open folder Documents", "Open my pictures"         |
| Open apps           | Spotify, WhatsApp, VS Code, Excel, Word, PowerPoint |

---

## Project Structure

```
voice_assistant/
├── assistant.py          # Main orchestrator with wake-word detection
├── dataset.py            # Labelled command dataset (400+ examples, 35 intents)
├── model_trainer.py      # TF-IDF + Logistic Regression pipeline
├── command_executor.py   # OS-level command dispatcher (subprocess-safe)
├── slot_extractor.py     # Parameter extraction from commands
├── voice_io.py           # Microphone input & TTS output (hybrid cloud/local)
├── gui.py                # Dark-terminal GUI with confidence visualisation
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

**GUI mode (recommended):**
```bash
python gui.py
```

**CLI mode (with wake-word detection):**
```bash
python assistant.py
```

Say **"Hey Assistant"** to activate, then speak your command.
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
Voice Input (Google Web Speech API / PocketSphinx offline fallback / keyboard)
    │
    ▼
Wake-Word Detection  ("Hey Assistant" / "Sypher")
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
Intent Prediction  (with confidence score + probability distribution)
    │
    ▼
Slot Extraction  (query, folder name, app name)
    │
    ▼
Command Executor  (subprocess – cross-platform, injection-safe)
    │
    ▼
Voice Feedback  (pyttsx3 TTS)
```

---

## Extending the Assistant

1. **Add a new command** – add labelled examples to `dataset.py`
2. **Add a handler** – implement a function in `command_executor.py` and register it in `INTENT_HANDLERS`
3. **Add slot extraction** – if the intent needs parameters, add extraction logic in `slot_extractor.py`
4. **Re-train** – run `python model_trainer.py`

---

## Security

All OS-level commands use `subprocess.Popen` / `subprocess.run` with
**list-based arguments** (no shell interpolation). User input is never
concatenated into command strings, preventing shell injection attacks.

---

## References

* Salton & Buckley (1988) – TF-IDF Text Representation
* Pedregosa et al. (2011) – Scikit-learn Machine Learning Library
* Jurafsky & Martin (2009) – Speech and Language Processing
