"""
gui.py
─────────────────────────────────────────────────────────────────
Dark-terminal GUI for the AI Voice Assistant.
Continuous listening mode: click START → listens in a loop until
you say "stop" / "quit" / "goodbye" or click STOP.
Run:  python gui.py
─────────────────────────────────────────────────────────────────
"""

import sys
import os
import threading
import queue
import platform
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model_trainer    import load_model, preprocess
from command_executor import execute, INTENT_HANDLERS

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

try:
    import pyttsx3
    _tts = pyttsx3.init()
    _tts.setProperty("rate", 160)
    _tts.setProperty("volume", 0.9)
    TTS_AVAILABLE = True
except Exception:
    TTS_AVAILABLE = False

# ── Palette ──────────────────────────────────────────────────────
BG      = "#0a0c10"
PANEL   = "#10141c"
BORDER  = "#1e2530"
ACCENT  = "#00e5ff"
ACCENT2 = "#ff3d71"
ACCENT3 = "#39ff14"
TEXT_HI  = "#e8eaf0"
TEXT_MID = "#7a8499"
TEXT_DIM = "#3a4050"
FONT_MONO = "Courier"
FONT_UI   = "Helvetica"

CONFIDENCE_THRESHOLD = 0.40
STOP_WORDS = {"stop", "quit", "exit", "bye", "goodbye", "stop listening",
              "stop now", "pause", "that's all", "thats all"}
WIN_W, WIN_H = 780, 680


# ── TTS ───────────────────────────────────────────────────────────
def speak_async(text: str):
    if TTS_AVAILABLE:
        def _go():
            try:
                _tts.say(text)
                _tts.runAndWait()
            except Exception:
                pass
        threading.Thread(target=_go, daemon=True).start()


# ════════════════════════════════════════════════════════════════
# Animated pulse ring
# ════════════════════════════════════════════════════════════════
class PulseRing(tk.Canvas):
    def __init__(self, master, size=120, **kw):
        super().__init__(master, width=size, height=size,
                         bg=BG, highlightthickness=0, **kw)
        self.size = size
        self.cx = self.cy = size // 2
        self.r_base = size // 2 - 14
        self._phase  = 0.0
        self._active = False
        self._color  = ACCENT
        m = 4
        self.create_oval(m, m, size - m, size - m,
                         outline=BORDER, width=2, tags="border")
        self._animate()

    def _animate(self):
        self.delete("ring"); self.delete("dot"); self.delete("icon")
        if self._active:
            for i in range(3):
                p = (self._phase + i * 0.33) % 1.0
                r = int(self.r_base * (0.6 + 0.4 * p))
                w = max(1, int(3 * (1 - p)))
                self.create_oval(self.cx - r, self.cy - r,
                                 self.cx + r, self.cy + r,
                                 outline=self._color, width=w, tags="ring")
            self._phase = (self._phase + 0.025) % 1.0
            r2 = int(self.r_base * 0.45)
            self.create_oval(self.cx - r2, self.cy - r2,
                             self.cx + r2, self.cy + r2,
                             fill=self._color, outline="", tags="dot")
            self._draw_mic(self._color)
        else:
            r2 = int(self.r_base * 0.45)
            self.create_oval(self.cx - r2, self.cy - r2,
                             self.cx + r2, self.cy + r2,
                             fill=PANEL, outline=TEXT_DIM, width=2, tags="dot")
            self._draw_mic(TEXT_DIM)
        self.after(40, self._animate)

    def _draw_mic(self, color):
        cx, cy, mw, mh = self.cx, self.cy, 10, 14
        self.create_rectangle(cx - mw//2, cy - mh//2,
                               cx + mw//2, cy + mh//2,
                               fill=color, outline="", tags="icon")
        self.create_arc(cx - mw - 2, cy - 4, cx + mw + 2, cy + mh + 6,
                        start=0, extent=180, style=tk.ARC,
                        outline=color, width=2, tags="icon")
        self.create_line(cx, cy + mh//2 + 6, cx, cy + mh//2 + 12,
                         fill=color, width=2, tags="icon")
        self.create_line(cx - 6, cy + mh//2 + 12,
                         cx + 6, cy + mh//2 + 12,
                         fill=color, width=2, tags="icon")

    def set_active(self, active: bool, color=None):
        self._active = active
        self._color  = color if color else ACCENT
        self._phase  = 0.0


# ════════════════════════════════════════════════════════════════
# Log row
# ════════════════════════════════════════════════════════════════
class LogEntry:
    ICONS  = {"user": "▶", "assistant": "◆", "system": "⬡", "error": "✕"}
    COLORS = {"user": ACCENT, "assistant": ACCENT3,
              "system": TEXT_MID, "error": ACCENT2}

    def __init__(self, parent, role, text, intent="", conf=0):
        color = self.COLORS.get(role, TEXT_MID)
        row = tk.Frame(parent, bg=PANEL, pady=6, padx=10)
        row.pack(fill=tk.X, pady=2, padx=6)

        tk.Label(row, text=self.ICONS.get(role, "·"),
                 fg=color, bg=PANEL,
                 font=(FONT_MONO, 11, "bold"), width=2).pack(
                     side=tk.LEFT, anchor="n", padx=(0, 8))

        col = tk.Frame(row, bg=PANEL)
        col.pack(side=tk.LEFT, fill=tk.X, expand=True)

        hdr = tk.Frame(col, bg=PANEL)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text=role.upper(), fg=color, bg=PANEL,
                 font=(FONT_MONO, 8, "bold")).pack(side=tk.LEFT)
        if intent:
            tk.Label(hdr, text=f"  {intent}  ", fg=BG, bg=color,
                     font=(FONT_MONO, 7, "bold"), padx=2).pack(
                         side=tk.LEFT, padx=6)
        if conf:
            cc = (ACCENT3 if conf >= 0.65
                  else TEXT_MID if conf >= CONFIDENCE_THRESHOLD
                  else ACCENT2)
            tk.Label(hdr, text=f"{conf:.0%}", fg=cc, bg=PANEL,
                     font=(FONT_MONO, 8)).pack(side=tk.LEFT)

        tk.Label(col, text=text, fg=TEXT_HI, bg=PANEL,
                 font=(FONT_UI, 10), wraplength=520,
                 justify=tk.LEFT, anchor="w").pack(fill=tk.X, pady=(2, 0))


# ════════════════════════════════════════════════════════════════
# Main window
# ════════════════════════════════════════════════════════════════
class AssistantGUI(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("AI Voice Assistant")
        self.geometry(f"{WIN_W}x{WIN_H}")
        self.resizable(True, True)
        self.configure(bg=BG)
        self.minsize(620, 500)

        self._model      = None
        self._input_mode = tk.StringVar(value="voice")
        self._msg_queue  = queue.Queue()
        self._continuous = False
        self._stop_flag  = threading.Event()
        self._phrase_cnt = 0

        self._build_ui()
        self._load_model_async()
        self.after(100, self._poll_queue)

    # ── model ─────────────────────────────────────────────────────
    def _load_model_async(self):
        def _go():
            self._post("system", "Loading ML model …")
            try:
                self._model = load_model()
                self._post("system",
                    "Model ready.  Click  ▶ START  to begin continuous "
                    "listening, or switch to TEXT mode.")
            except Exception as e:
                self._post("error", f"Model load failed: {e}")
        threading.Thread(target=_go, daemon=True).start()

    # ── build UI ──────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=PANEL, height=54)
        hdr.pack(fill=tk.X); hdr.pack_propagate(False)
        tk.Label(hdr, text="  ◈  AI VOICE ASSISTANT",
                 fg=ACCENT, bg=PANEL,
                 font=(FONT_MONO, 13, "bold")).pack(
                     side=tk.LEFT, padx=16, pady=12)
        tk.Label(hdr, text=f"{platform.system().upper()}  ●  READY",
                 fg=TEXT_MID, bg=PANEL,
                 font=(FONT_MONO, 8)).pack(side=tk.RIGHT, padx=16)
        tk.Frame(self, bg=ACCENT, height=2).pack(fill=tk.X)

        body = tk.Frame(self, bg=BG)
        body.pack(fill=tk.BOTH, expand=True)

        # ── LEFT ──
        left = tk.Frame(body, bg=BG, width=160)
        left.pack(side=tk.LEFT, fill=tk.Y); left.pack_propagate(False)

        self._pulse = PulseRing(left, size=120)
        self._pulse.pack(pady=(30, 10))

        self._status_lbl = tk.Label(left, text="IDLE", fg=TEXT_DIM, bg=BG,
                                     font=(FONT_MONO, 8, "bold"))
        self._status_lbl.pack()

        # live phrase counter badge
        self._badge = tk.Label(left, text="", fg=BG, bg=ACCENT3,
                                font=(FONT_MONO, 7, "bold"), padx=6, pady=2)

        # mode toggle
        mf = tk.Frame(left, bg=BG)
        mf.pack(pady=(20, 0))
        tk.Label(mf, text="INPUT MODE", fg=TEXT_DIM, bg=BG,
                 font=(FONT_MONO, 7, "bold")).pack(pady=(0, 8))
        for mode, label in [("voice", "🎙  VOICE"), ("text", "⌨  TEXT")]:
            tk.Radiobutton(
                mf, text=label, variable=self._input_mode, value=mode,
                fg=TEXT_MID, selectcolor=PANEL, bg=BG,
                activebackground=BG, activeforeground=ACCENT,
                font=(FONT_MONO, 9), indicatoron=0, relief=tk.FLAT,
                bd=0, padx=12, pady=6, width=10, cursor="hand2",
                command=self._on_mode_change,
            ).pack(pady=3)

        # commands list (interactive dropdowns)
        cf = tk.Frame(left, bg=BG)
        cf.pack(pady=(20, 0), padx=10, fill=tk.BOTH, expand=True)
        tk.Label(cf, text="COMMANDS", fg=TEXT_DIM, bg=BG,
                 font=(FONT_MONO, 7, "bold")).pack(anchor="w", pady=(0, 4))

        cmd_canvas = tk.Canvas(cf, bg=BG, highlightthickness=0, width=140)
        cmd_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cmd_inner = tk.Frame(cmd_canvas, bg=BG)
        cmd_canvas.create_window((0, 0), window=cmd_inner, anchor="nw")
        cmd_inner.bind("<Configure>", lambda e: cmd_canvas.configure(
            scrollregion=cmd_canvas.bbox("all")))
        cmd_canvas.bind("<MouseWheel>",
            lambda e: cmd_canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        cmd_groups = [
            ("CORE", [
                "open browser", "open calculator", "file explorer",
                "open notepad", "task manager", "close app",
                "volume up/down", "mute", "screenshot",
                "shutdown", "restart", "hello",
            ]),
            ("WEB", [
                "search google", "open youtube", "open gmail",
            ]),
            ("FILES", [
                "open downloads", "open desktop", "create folder",
            ]),
            ("APPS", [
                "open spotify", "open whatsapp", "open vscode",
                "open excel", "open word", "open powerpoint",
            ]),
        ]

        for group_name, cmds in cmd_groups:
            # Container for each dropdown group
            group_frame = tk.Frame(cmd_inner, bg=BG)
            group_frame.pack(fill=tk.X, pady=(2, 0))

            # Items frame (hidden by default)
            items_frame = tk.Frame(group_frame, bg=BG)
            for c in cmds:
                tk.Label(items_frame, text=f"  › {c}", fg=TEXT_DIM, bg=BG,
                         font=(FONT_MONO, 7), anchor="w").pack(fill=tk.X)

            # State tracker
            expanded = tk.BooleanVar(value=False)

            # Header button
            hdr_btn = tk.Label(
                group_frame,
                text=f"  ▸  {group_name}",
                fg=TEXT_MID, bg=BG,
                font=(FONT_MONO, 8, "bold"),
                anchor="w", cursor="hand2",
                padx=2, pady=4,
            )
            hdr_btn.pack(fill=tk.X)

            # Separator line under header
            sep = tk.Frame(group_frame, bg=BORDER, height=1)
            sep.pack(fill=tk.X, padx=4)

            def _toggle(ev=None, _hdr=hdr_btn, _items=items_frame,
                        _exp=expanded, _name=group_name):
                if _exp.get():
                    _items.pack_forget()
                    _hdr.config(text=f"  ▸  {_name}")
                    _exp.set(False)
                else:
                    _items.pack(fill=tk.X)
                    _hdr.config(text=f"  ▾  {_name}")
                    _exp.set(True)

            hdr_btn.bind("<Button-1>", _toggle)
            hdr_btn.bind("<Enter>",
                lambda e, h=hdr_btn: h.config(fg=ACCENT, bg="#131820"))
            hdr_btn.bind("<Leave>",
                lambda e, h=hdr_btn: h.config(fg=TEXT_MID, bg=BG))

        tk.Frame(body, bg=BORDER, width=1).pack(side=tk.LEFT, fill=tk.Y)

        # ── RIGHT ──
        right = tk.Frame(body, bg=BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        log_outer = tk.Frame(right, bg=BG)
        log_outer.pack(fill=tk.BOTH, expand=True)
        self._canvas = tk.Canvas(log_outer, bg=BG, highlightthickness=0)
        sb = tk.Scrollbar(log_outer, orient=tk.VERTICAL,
                          command=self._canvas.yview,
                          bg=PANEL, troughcolor=BG)
        self._canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._log_frame = tk.Frame(self._canvas, bg=BG)
        self._log_win   = self._canvas.create_window(
            (0, 0), window=self._log_frame, anchor="nw")
        self._log_frame.bind("<Configure>", lambda e: self._canvas.configure(
            scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>", lambda e: self._canvas.itemconfig(
            self._log_win, width=e.width))

        self._add_log("system",
            "Click  ▶ START  to begin continuous listening, "
            "or switch to TEXT mode below.", "", 0)

        # ── Bottom bar ──
        tk.Frame(right, bg=ACCENT, height=2).pack(fill=tk.X)
        bottom = tk.Frame(right, bg=PANEL, height=70)
        bottom.pack(fill=tk.X); bottom.pack_propagate(False)

        # text entry (voice mode: hidden)
        self._entry_frame = tk.Frame(bottom, bg=PANEL)
        self._entry = tk.Entry(
            self._entry_frame,
            bg="#0f1520", fg=TEXT_HI, insertbackground=ACCENT,
            relief=tk.FLAT, font=(FONT_MONO, 11),
            bd=0, highlightthickness=1,
            highlightcolor=ACCENT, highlightbackground=BORDER)
        self._entry.pack(fill=tk.BOTH, expand=True, ipady=6, padx=2)
        self._entry.bind("<Return>", lambda e: self._submit_text())

        # CLR
        tk.Button(bottom, text="CLR",
                  fg=TEXT_DIM, bg=PANEL,
                  activebackground=BORDER, activeforeground=TEXT_MID,
                  font=(FONT_MONO, 8), relief=tk.FLAT,
                  cursor="hand2", bd=0, padx=8,
                  command=self._clear_log).pack(
                      side=tk.RIGHT, pady=10, padx=4)

        # STOP button
        self._stop_btn = tk.Button(
            bottom, text="  ■  STOP  ",
            fg=ACCENT2, bg=PANEL,
            activebackground=BORDER, activeforeground=ACCENT2,
            font=(FONT_MONO, 10, "bold"),
            relief=tk.FLAT, cursor="hand2",
            bd=0, padx=12, pady=0,
            state=tk.DISABLED,
            command=self._stop_listening)
        self._stop_btn.pack(side=tk.RIGHT, padx=4, pady=10,
                             ipadx=4, ipady=4)

        # START / SEND button
        self._action_btn = tk.Button(
            bottom,
            text="  ▶  START  ",
            fg=BG, bg=ACCENT,
            activebackground=ACCENT, activeforeground=BG,
            font=(FONT_MONO, 10, "bold"),
            relief=tk.FLAT, cursor="hand2",
            bd=0, padx=16, pady=0,
            command=self._on_action_btn)
        self._action_btn.pack(side=tk.RIGHT, padx=4, pady=10,
                               ipadx=4, ipady=4)

        # Status bar
        self._statusbar = tk.Label(self, text="  Ready",
                                    fg=TEXT_DIM, bg=PANEL,
                                    font=(FONT_MONO, 8), anchor="w")
        self._statusbar.pack(fill=tk.X, side=tk.BOTTOM)

    # ── mode toggle ───────────────────────────────────────────────
    def _on_mode_change(self):
        if self._continuous:
            self._stop_listening()
        mode = self._input_mode.get()
        if mode == "voice":
            self._entry_frame.pack_forget()
            self._action_btn.config(text="  ▶  START  ", bg=ACCENT)
            self._stop_btn.pack(side=tk.RIGHT, padx=4, pady=10,
                                 ipadx=4, ipady=4)
        else:
            self._stop_btn.pack_forget()
            self._entry_frame.pack(side=tk.LEFT, fill=tk.BOTH,
                                   expand=True, padx=10, pady=10)
            self._action_btn.config(text="  ➤  SEND  ", bg=ACCENT)
            self._entry.focus_set()

    # ── logging ───────────────────────────────────────────────────
    def _add_log(self, role, text, intent="", conf=0):
        LogEntry(self._log_frame, role, text, intent, conf)
        self.after(50, lambda: self._canvas.yview_moveto(1.0))

    def _clear_log(self):
        for w in self._log_frame.winfo_children():
            w.destroy()
        self._add_log("system", "Log cleared.", "", 0)

    # ── queue ─────────────────────────────────────────────────────
    def _post(self, role, text, intent="", conf=0.0):
        self._msg_queue.put((role, text, intent, conf))

    def _poll_queue(self):
        try:
            while True:
                role, text, intent, conf = self._msg_queue.get_nowait()
                self._add_log(role, text, intent, conf)
                self._statusbar.config(text=f"  {text[:90]}")
        except queue.Empty:
            pass
        self.after(80, self._poll_queue)

    def _set_status(self, text, color=TEXT_DIM):
        self._status_lbl.config(text=text, fg=color)
        self._statusbar.config(text=f"  {text}")

    # ── button ────────────────────────────────────────────────────
    def _on_action_btn(self):
        if self._input_mode.get() == "text":
            self._submit_text()
        elif not self._continuous:
            self._begin_continuous()

    # ── text mode ─────────────────────────────────────────────────
    def _submit_text(self):
        text = self._entry.get().strip()
        if not text:
            return
        self._entry.delete(0, tk.END)
        self._process_command(text, block=False)

    # ══════════════════════════════════════════════════════════════
    # Continuous listen
    # ══════════════════════════════════════════════════════════════
    def _begin_continuous(self):
        if not SR_AVAILABLE:
            self._post("error",
                "SpeechRecognition not installed.  "
                "Run:  pip install SpeechRecognition pyaudio")
            return
        self._continuous  = True
        self._phrase_cnt  = 0
        self._stop_flag.clear()

        self._action_btn.config(state=tk.DISABLED,
                                text="  ● LIVE  ", bg=ACCENT2)
        self._stop_btn.config(state=tk.NORMAL)
        self._pulse.set_active(True, color=ACCENT)
        self._set_status("LISTENING …", ACCENT)
        self._post("system",
            "Continuous listening started.  "
            "Say  'stop'  or click  ■ STOP  to end.")

        threading.Thread(target=self._continuous_loop, daemon=True).start()

    def _stop_listening(self):
        self._stop_flag.set()

    def _continuous_loop(self):
        """Background thread: loop listen → classify → execute."""
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = True

        try:
            # Calibrate once
            with sr.Microphone() as src:
                recognizer.adjust_for_ambient_noise(src, duration=0.8)

            while not self._stop_flag.is_set():
                # ── listening state ──
                self.after(0, lambda: (
                    self._pulse.set_active(True, color=ACCENT),
                    self._set_status("LISTENING …", ACCENT)
                ))

                audio = None
                try:
                    with sr.Microphone() as src:
                        audio = recognizer.listen(
                            src, timeout=4, phrase_time_limit=8)
                except sr.WaitTimeoutError:
                    # silence — loop and re-check flag
                    continue
                except Exception as e:
                    self._post("error", f"Mic error: {e}")
                    break

                if self._stop_flag.is_set():
                    break

                # ── recognise ──
                text = None
                try:
                    text = recognizer.recognize_google(audio)
                except sr.UnknownValueError:
                    self._post("system", "Couldn't understand — listening again …")
                    continue
                except sr.RequestError as e:
                    self._post("error", f"Speech API error: {e}")
                    break

                if not text:
                    continue

                # ── stop-word check ──
                if text.lower().strip() in STOP_WORDS:
                    self._post("system", f"Heard '{text}' — stopping.")
                    speak_async("Stopping. Goodbye!")
                    break

                # ── process ──
                self._phrase_cnt += 1
                cnt = self._phrase_cnt
                self.after(0, lambda c=cnt: (
                    self._badge.config(text=f" ● {c} cmd{'s' if c>1 else ''} "),
                    self._badge.pack(pady=(6, 0))
                ))
                self.after(0, lambda: self._pulse.set_active(True, color=ACCENT3))
                self.after(0, lambda: self._set_status("PROCESSING …", ACCENT3))

                # run synchronously inside this thread
                self._process_command(text, block=True)

        finally:
            self._continuous = False
            self._stop_flag.clear()
            self.after(0, self._reset_after_stop)

    def _reset_after_stop(self):
        self._pulse.set_active(False)
        self._badge.pack_forget()
        self._set_status("IDLE", TEXT_DIM)
        self._action_btn.config(state=tk.NORMAL,
                                text="  ▶  START  ", bg=ACCENT)
        self._stop_btn.config(state=tk.DISABLED)
        self._post("system", "Continuous listening stopped.")

    # ══════════════════════════════════════════════════════════════
    # NLP + execution
    # ══════════════════════════════════════════════════════════════
    def _process_command(self, text: str, block: bool = False):
        if self._model is None:
            self._post("error", "Model not loaded yet. Please wait.")
            return

        def _run():
            self._post("user", text)
            processed = preprocess(text)
            proba   = self._model.predict_proba([processed])[0]
            classes = self._model.classes_
            idx     = proba.argmax()
            intent  = classes[idx]
            conf    = float(proba[idx])

            if conf < CONFIDENCE_THRESHOLD:
                msg = "I'm not sure what you meant. Could you rephrase?"
                self._post("assistant", msg, "unknown", conf)
                speak_async(msg)
                return

            response = execute(intent)
            self._post("assistant", response, intent, conf)
            speak_async(response)

        if block:
            _run()
        else:
            threading.Thread(target=_run, daemon=True).start()


# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = AssistantGUI()
    app.mainloop()