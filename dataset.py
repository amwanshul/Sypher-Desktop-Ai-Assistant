"""
Command Dataset for Intent Classification  v4
~240 examples across 25 intent classes.
Fixes:
  - Removed 'close window' from close_app  (conflicts with open_desktop)
  - Removed 'open folder' from open_file_explorer  (conflicts with create_folder)
  - Removed 'open messages' from open_whatsapp  (too generic)
  - Tightened examples so each intent has clearly distinct phrasing
"""

COMMAND_DATASET = [

    # ── open_browser ─────────────────────────────────────────────
    ("open browser",           "open_browser"),
    ("launch browser",         "open_browser"),
    ("start browser",          "open_browser"),
    ("open web browser",       "open_browser"),
    ("open internet browser",  "open_browser"),
    ("browse the internet",    "open_browser"),
    ("go to browser",          "open_browser"),
    ("open edge",              "open_browser"),
    ("open the internet",      "open_browser"),

    # ── open_calculator ───────────────────────────────────────────
    ("open calculator",        "open_calculator"),
    ("launch calculator",      "open_calculator"),
    ("start calculator",       "open_calculator"),
    ("open calc",              "open_calculator"),
    ("start calc",             "open_calculator"),
    ("launch calc",            "open_calculator"),
    ("i need a calculator",    "open_calculator"),
    ("run calculator",         "open_calculator"),
    ("calculator please",      "open_calculator"),

    # ── open_file_explorer ────────────────────────────────────────
    ("open file explorer",     "open_file_explorer"),
    ("launch file explorer",   "open_file_explorer"),
    ("open explorer",          "open_file_explorer"),
    ("show files",             "open_file_explorer"),
    ("browse files",           "open_file_explorer"),
    ("open my files",          "open_file_explorer"),
    ("launch explorer",        "open_file_explorer"),
    ("file manager",           "open_file_explorer"),
    ("open this pc",           "open_file_explorer"),
    ("show my computer",       "open_file_explorer"),
    ("open windows explorer",  "open_file_explorer"),

    # ── open_notepad ─────────────────────────────────────────────
    ("open notepad",           "open_notepad"),
    ("launch notepad",         "open_notepad"),
    ("start notepad",          "open_notepad"),
    ("open text editor",       "open_notepad"),
    ("start text editor",      "open_notepad"),
    ("open writing app",       "open_notepad"),
    ("open a text file",       "open_notepad"),

    # ── open_task_manager ─────────────────────────────────────────
    ("open task manager",      "open_task_manager"),
    ("launch task manager",    "open_task_manager"),
    ("show running processes", "open_task_manager"),
    ("check running apps",     "open_task_manager"),
    ("open process manager",   "open_task_manager"),
    ("show cpu usage",         "open_task_manager"),
    ("open system monitor",    "open_task_manager"),
    ("check system performance","open_task_manager"),

    # ── close_app ────────────────────────────────────────────────
    # NOTE: no 'close window' — conflicts with open_desktop
    ("close app",              "close_app"),
    ("close application",      "close_app"),
    ("close chrome",           "close_app"),
    ("close browser",          "close_app"),
    ("close firefox",          "close_app"),
    ("close notepad",          "close_app"),
    ("close excel",            "close_app"),
    ("close word",             "close_app"),
    ("close spotify",          "close_app"),
    ("exit application",       "close_app"),
    ("exit browser",           "close_app"),
    ("terminate app",          "close_app"),
    ("kill application",       "close_app"),
    ("quit application",       "close_app"),

    # ── shutdown ──────────────────────────────────────────────────
    ("shutdown system",        "shutdown"),
    ("shutdown computer",      "shutdown"),
    ("turn off computer",      "shutdown"),
    ("power off",              "shutdown"),
    ("shut down",              "shutdown"),
    ("switch off computer",    "shutdown"),
    ("turn off system",        "shutdown"),
    ("shutdown the system",    "shutdown"),
    ("power down computer",    "shutdown"),
    ("switch off system",      "shutdown"),
    ("turn off the pc",        "shutdown"),

    # ── restart ───────────────────────────────────────────────────
    ("restart system",         "restart"),
    ("restart computer",       "restart"),
    ("reboot system",          "restart"),
    ("reboot computer",        "restart"),
    ("restart the computer",   "restart"),
    ("reboot the system",      "restart"),
    ("restart machine",        "restart"),
    ("reboot machine",         "restart"),
    ("restart now",            "restart"),
    ("reboot now",             "restart"),
    ("restart the pc",         "restart"),

    # ── volume_up ─────────────────────────────────────────────────
    ("increase volume",        "volume_up"),
    ("volume up",              "volume_up"),
    ("turn up volume",         "volume_up"),
    ("louder",                 "volume_up"),
    ("raise volume",           "volume_up"),
    ("increase sound",         "volume_up"),
    ("make it louder",         "volume_up"),
    ("turn up the sound",      "volume_up"),

    # ── volume_down ───────────────────────────────────────────────
    ("decrease volume",        "volume_down"),
    ("volume down",            "volume_down"),
    ("turn down volume",       "volume_down"),
    ("quieter",                "volume_down"),
    ("lower volume",           "volume_down"),
    ("decrease sound",         "volume_down"),
    ("make it quieter",        "volume_down"),
    ("turn down the sound",    "volume_down"),

    # ── mute ─────────────────────────────────────────────────────
    ("mute",                   "mute"),
    ("mute volume",            "mute"),
    ("mute sound",             "mute"),
    ("silence",                "mute"),
    ("turn off sound",         "mute"),
    ("no sound",               "mute"),
    ("toggle mute",            "mute"),

    # ── take_screenshot ───────────────────────────────────────────
    ("take screenshot",        "take_screenshot"),
    ("capture screen",         "take_screenshot"),
    ("screenshot",             "take_screenshot"),
    ("capture screenshot",     "take_screenshot"),
    ("take a screenshot",      "take_screenshot"),
    ("snap screen",            "take_screenshot"),
    ("save screenshot",        "take_screenshot"),
    ("print screen",           "take_screenshot"),
    ("capture my screen",      "take_screenshot"),

    # ── greet ────────────────────────────────────────────────────
    ("hello",                  "greet"),
    ("hi",                     "greet"),
    ("hey",                    "greet"),
    ("good morning",           "greet"),
    ("good evening",           "greet"),
    ("how are you",            "greet"),
    ("what can you do",        "greet"),
    ("what are your commands", "greet"),
    ("show commands",          "greet"),
    ("help",                   "greet"),

    # ══════════════════════════════════════════════════════════════
    # Web & Search
    # ══════════════════════════════════════════════════════════════

    # search_google
    ("search google",          "search_google"),
    ("google search",          "search_google"),
    ("search on google",       "search_google"),
    ("look it up on google",   "search_google"),
    ("open google",            "search_google"),
    ("go to google",           "search_google"),
    ("search the web",         "search_google"),
    ("google it",              "search_google"),
    ("do a google search",     "search_google"),
    ("search online",          "search_google"),

    # open_youtube
    ("open youtube",           "open_youtube"),
    ("launch youtube",         "open_youtube"),
    ("go to youtube",          "open_youtube"),
    ("start youtube",          "open_youtube"),
    ("play youtube",           "open_youtube"),
    ("youtube please",         "open_youtube"),
    ("watch youtube",          "open_youtube"),
    ("open video site",        "open_youtube"),
    ("youtube",                "open_youtube"),
    ("go to youtube website",  "open_youtube"),

    # open_gmail
    ("open gmail",             "open_gmail"),
    ("launch gmail",           "open_gmail"),
    ("go to gmail",            "open_gmail"),
    ("check my email",         "open_gmail"),
    ("open my email",          "open_gmail"),
    ("check email",            "open_gmail"),
    ("show my inbox",          "open_gmail"),
    ("read my email",          "open_gmail"),
    ("open inbox",             "open_gmail"),
    ("open google mail",       "open_gmail"),

    # ══════════════════════════════════════════════════════════════
    # File & Folder
    # ══════════════════════════════════════════════════════════════

    # open_downloads
    ("open downloads",         "open_downloads"),
    ("go to downloads",        "open_downloads"),
    ("show downloads",         "open_downloads"),
    ("open downloads folder",  "open_downloads"),
    ("my downloads",           "open_downloads"),
    ("launch downloads",       "open_downloads"),
    ("open downloaded files",  "open_downloads"),
    ("where are my downloads", "open_downloads"),
    ("show downloaded files",  "open_downloads"),

    # open_desktop
    # NOTE: no 'minimize all windows' — use specific desktop navigation phrases
    ("open desktop",           "open_desktop"),
    ("go to desktop",          "open_desktop"),
    ("show desktop",           "open_desktop"),
    ("show my desktop",        "open_desktop"),
    ("back to desktop",        "open_desktop"),
    ("open desktop folder",    "open_desktop"),
    ("go to home screen",      "open_desktop"),
    ("show home screen",       "open_desktop"),

    # create_folder
    # NOTE: no 'open folder' — conflicts with open_file_explorer
    ("create folder",          "create_folder"),
    ("make a folder",          "create_folder"),
    ("new folder",             "create_folder"),
    ("create new folder",      "create_folder"),
    ("make new folder",        "create_folder"),
    ("add a folder",           "create_folder"),
    ("create directory",       "create_folder"),
    ("make directory",         "create_folder"),
    ("create a new folder",    "create_folder"),

    # ══════════════════════════════════════════════════════════════
    # Apps
    # ══════════════════════════════════════════════════════════════

    # open_spotify
    ("open spotify",           "open_spotify"),
    ("launch spotify",         "open_spotify"),
    ("start spotify",          "open_spotify"),
    ("play spotify",           "open_spotify"),
    ("play music",             "open_spotify"),
    ("start music",            "open_spotify"),
    ("open music player",      "open_spotify"),
    ("play some music",        "open_spotify"),
    ("put on music",           "open_spotify"),
    ("open spotify app",       "open_spotify"),

    # open_whatsapp
    # NOTE: removed 'open messages' — too generic
    ("open whatsapp",          "open_whatsapp"),
    ("launch whatsapp",        "open_whatsapp"),
    ("start whatsapp",         "open_whatsapp"),
    ("open whatsapp web",      "open_whatsapp"),
    ("go to whatsapp",         "open_whatsapp"),
    ("check whatsapp",         "open_whatsapp"),
    ("open telegram",          "open_whatsapp"),
    ("launch telegram",        "open_whatsapp"),
    ("open chat app",          "open_whatsapp"),
    ("open whatsapp desktop",  "open_whatsapp"),

    # open_vscode
    ("open vs code",           "open_vscode"),
    ("launch vs code",         "open_vscode"),
    ("start vs code",          "open_vscode"),
    ("open visual studio code","open_vscode"),
    ("open code editor",       "open_vscode"),
    ("launch code editor",     "open_vscode"),
    ("open vscode",            "open_vscode"),
    ("start coding",           "open_vscode"),
    ("open my editor",         "open_vscode"),
    ("launch visual studio",   "open_vscode"),

    # open_excel
    ("open excel",             "open_excel"),
    ("launch excel",           "open_excel"),
    ("start excel",            "open_excel"),
    ("open spreadsheet",       "open_excel"),
    ("open microsoft excel",   "open_excel"),
    ("launch spreadsheet",     "open_excel"),
    ("open excel app",         "open_excel"),
    ("start spreadsheet",      "open_excel"),

    # open_word
    ("open word",              "open_word"),
    ("launch word",            "open_word"),
    ("start word",             "open_word"),
    ("open microsoft word",    "open_word"),
    ("open document editor",   "open_word"),
    ("open word processor",    "open_word"),
    ("open ms word",           "open_word"),
    ("launch word document",   "open_word"),

    # open_powerpoint
    ("open powerpoint",        "open_powerpoint"),
    ("launch powerpoint",      "open_powerpoint"),
    ("start powerpoint",       "open_powerpoint"),
    ("open microsoft powerpoint", "open_powerpoint"),
    ("open presentation app",  "open_powerpoint"),
    ("launch presentation",    "open_powerpoint"),
    ("open slides",            "open_powerpoint"),
    ("open ms powerpoint",     "open_powerpoint"),
    ("start presentation",     "open_powerpoint"),
]