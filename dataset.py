"""
Command Dataset for Intent Classification  v5
~400 examples across 35 intent classes.
New in v5:
  - search_web        : parameterised web search  ("search for cats", "google leetcode")
  - search_youtube    : parameterised YouTube search ("youtube search cats", "search on youtube for music")
  - get_time          : tell current time
  - get_date          : tell current date
  - get_battery       : show battery percentage
  - get_ip_address    : show IP address
  - open_settings     : open system Settings
  - lock_screen       : lock the computer
  - empty_recycle_bin : empty Recycle Bin / Trash
  - open_cmd          : open terminal / command prompt
  - open_folder_path  : open a specific named folder (Documents, Pictures …)
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
    # Web & Search  (parameterised — slot extractor pulls the query)
    # ══════════════════════════════════════════════════════════════

    # ── search_web  (browser + Google search with query) ─────────
    ("search for python tutorials",       "search_web"),
    ("search for leetcode",               "search_web"),
    ("search for machine learning",       "search_web"),
    ("google leetcode",                   "search_web"),
    ("google python documentation",       "search_web"),
    ("google how to cook pasta",          "search_web"),
    ("open browser and search for leetcode",     "search_web"),
    ("open browser and search for weather",      "search_web"),
    ("open browser and search for recipes",      "search_web"),
    ("search the web for javascript",     "search_web"),
    ("look up artificial intelligence",   "search_web"),
    ("look up how to code",              "search_web"),
    ("search online for best laptops",    "search_web"),
    ("web search for python",             "search_web"),
    ("find information about mars",       "search_web"),
    ("search for news",                   "search_web"),
    ("browser search for openai",         "search_web"),
    ("search for stack overflow",         "search_web"),
    ("search for github",                 "search_web"),
    ("search for react tutorial",         "search_web"),

    # ── search_google  (just opens Google, no query) ─────────────
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

    # ── search_youtube  (YouTube search with query) ──────────────
    ("search youtube for music",                  "search_youtube"),
    ("search youtube for coding tutorials",       "search_youtube"),
    ("search youtube for funny videos",           "search_youtube"),
    ("open youtube and search for cats",          "search_youtube"),
    ("open youtube and search for music",         "search_youtube"),
    ("open youtube and search for python tutorial","search_youtube"),
    ("open youtube and search for gaming",        "search_youtube"),
    ("youtube search for recipes",                "search_youtube"),
    ("youtube search for workout",                "search_youtube"),
    ("search on youtube for travel vlogs",        "search_youtube"),
    ("find on youtube how to draw",               "search_youtube"),
    ("look up on youtube machine learning",       "search_youtube"),
    ("play on youtube lo-fi music",               "search_youtube"),
    ("youtube find cooking videos",               "search_youtube"),
    ("search videos for react tutorial",          "search_youtube"),
    ("find videos about space",                   "search_youtube"),
    ("look for videos about fitness",             "search_youtube"),

    # ── open_youtube  (just opens YouTube, no query) ─────────────
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

    # ── open_gmail ────────────────────────────────────────────────
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

    # ── open_downloads ────────────────────────────────────────────
    ("open downloads",         "open_downloads"),
    ("go to downloads",        "open_downloads"),
    ("show downloads",         "open_downloads"),
    ("open downloads folder",  "open_downloads"),
    ("my downloads",           "open_downloads"),
    ("launch downloads",       "open_downloads"),
    ("open downloaded files",  "open_downloads"),
    ("where are my downloads", "open_downloads"),
    ("show downloaded files",  "open_downloads"),

    # ── open_desktop ──────────────────────────────────────────────
    ("open desktop",           "open_desktop"),
    ("go to desktop",          "open_desktop"),
    ("show desktop",           "open_desktop"),
    ("show my desktop",        "open_desktop"),
    ("back to desktop",        "open_desktop"),
    ("open desktop folder",    "open_desktop"),
    ("go to home screen",      "open_desktop"),
    ("show home screen",       "open_desktop"),

    # ── create_folder ─────────────────────────────────────────────
    ("create folder",          "create_folder"),
    ("make a folder",          "create_folder"),
    ("new folder",             "create_folder"),
    ("create new folder",      "create_folder"),
    ("make new folder",        "create_folder"),
    ("add a folder",           "create_folder"),
    ("create directory",       "create_folder"),
    ("make directory",         "create_folder"),
    ("create a new folder",    "create_folder"),

    # ── open_folder_path  (parameterised — slot extractor pulls folder name) ──
    ("open folder documents",          "open_folder_path"),
    ("open folder pictures",           "open_folder_path"),
    ("open folder music",              "open_folder_path"),
    ("open folder videos",             "open_folder_path"),
    ("go to documents folder",         "open_folder_path"),
    ("go to pictures folder",          "open_folder_path"),
    ("go to my documents",             "open_folder_path"),
    ("open my documents",              "open_folder_path"),
    ("open my pictures",               "open_folder_path"),
    ("open my music",                  "open_folder_path"),
    ("open my videos",                 "open_folder_path"),
    ("navigate to documents",          "open_folder_path"),
    ("navigate to pictures",           "open_folder_path"),
    ("show me my documents folder",    "open_folder_path"),
    ("browse documents folder",        "open_folder_path"),
    ("browse my pictures",             "open_folder_path"),

    # ══════════════════════════════════════════════════════════════
    # Apps
    # ══════════════════════════════════════════════════════════════

    # ── open_spotify ──────────────────────────────────────────────
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

    # ── open_whatsapp ─────────────────────────────────────────────
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

    # ── open_vscode ───────────────────────────────────────────────
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

    # ── open_excel ────────────────────────────────────────────────
    ("open excel",             "open_excel"),
    ("launch excel",           "open_excel"),
    ("start excel",            "open_excel"),
    ("open spreadsheet",       "open_excel"),
    ("open microsoft excel",   "open_excel"),
    ("launch spreadsheet",     "open_excel"),
    ("open excel app",         "open_excel"),
    ("start spreadsheet",      "open_excel"),

    # ── open_word ─────────────────────────────────────────────────
    ("open word",              "open_word"),
    ("launch word",            "open_word"),
    ("start word",             "open_word"),
    ("open microsoft word",    "open_word"),
    ("open document editor",   "open_word"),
    ("open word processor",    "open_word"),
    ("open ms word",           "open_word"),
    ("launch word document",   "open_word"),

    # ── open_powerpoint ───────────────────────────────────────────
    ("open powerpoint",        "open_powerpoint"),
    ("launch powerpoint",      "open_powerpoint"),
    ("start powerpoint",       "open_powerpoint"),
    ("open microsoft powerpoint", "open_powerpoint"),
    ("open presentation app",  "open_powerpoint"),
    ("launch presentation",    "open_powerpoint"),
    ("open slides",            "open_powerpoint"),
    ("open ms powerpoint",     "open_powerpoint"),
    ("start presentation",     "open_powerpoint"),

    # ══════════════════════════════════════════════════════════════
    # System / Internal Tasks
    # ══════════════════════════════════════════════════════════════

    # ── get_time ──────────────────────────────────────────────────
    ("what time is it",        "get_time"),
    ("tell me the time",       "get_time"),
    ("current time",           "get_time"),
    ("what is the time",       "get_time"),
    ("check the time",         "get_time"),
    ("time please",            "get_time"),
    ("show me the time",       "get_time"),
    ("what's the time",        "get_time"),
    ("give me the time",       "get_time"),

    # ── get_date ──────────────────────────────────────────────────
    ("what is today's date",   "get_date"),
    ("tell me the date",       "get_date"),
    ("current date",           "get_date"),
    ("what day is it",         "get_date"),
    ("what date is it",        "get_date"),
    ("today's date",           "get_date"),
    ("show me the date",       "get_date"),
    ("what is the date today", "get_date"),
    ("date please",            "get_date"),

    # ── get_battery ───────────────────────────────────────────────
    ("battery level",          "get_battery"),
    ("check battery",          "get_battery"),
    ("how much battery",       "get_battery"),
    ("how much charge",        "get_battery"),
    ("battery status",         "get_battery"),
    ("show battery",           "get_battery"),
    ("battery percentage",     "get_battery"),
    ("what is my battery",     "get_battery"),
    ("check charge level",     "get_battery"),

    # ── get_ip_address ────────────────────────────────────────────
    ("what is my ip",          "get_ip_address"),
    ("show my ip address",     "get_ip_address"),
    ("what's my ip address",   "get_ip_address"),
    ("get my ip",              "get_ip_address"),
    ("check my ip",            "get_ip_address"),
    ("ip address",             "get_ip_address"),
    ("show ip",                "get_ip_address"),
    ("my ip address",          "get_ip_address"),
    ("tell me my ip",          "get_ip_address"),

    # ── open_settings ─────────────────────────────────────────────
    ("open settings",          "open_settings"),
    ("launch settings",        "open_settings"),
    ("system settings",        "open_settings"),
    ("open system preferences","open_settings"),
    ("go to settings",         "open_settings"),
    ("windows settings",       "open_settings"),
    ("open control panel",     "open_settings"),
    ("show settings",          "open_settings"),
    ("open preferences",       "open_settings"),

    # ── lock_screen ───────────────────────────────────────────────
    ("lock screen",            "lock_screen"),
    ("lock my computer",       "lock_screen"),
    ("lock the pc",            "lock_screen"),
    ("lock my pc",             "lock_screen"),
    ("lock workstation",       "lock_screen"),
    ("lock this computer",     "lock_screen"),
    ("lock my screen",         "lock_screen"),
    ("lock the screen",        "lock_screen"),

    # ── empty_recycle_bin ─────────────────────────────────────────
    ("empty recycle bin",      "empty_recycle_bin"),
    ("clear recycle bin",      "empty_recycle_bin"),
    ("empty trash",            "empty_recycle_bin"),
    ("clear trash",            "empty_recycle_bin"),
    ("delete recycle bin",     "empty_recycle_bin"),
    ("clean recycle bin",      "empty_recycle_bin"),
    ("empty the trash",        "empty_recycle_bin"),
    ("clean up recycle bin",   "empty_recycle_bin"),

    # ── open_cmd ──────────────────────────────────────────────────
    ("open command prompt",    "open_cmd"),
    ("open terminal",          "open_cmd"),
    ("launch command prompt",  "open_cmd"),
    ("launch terminal",        "open_cmd"),
    ("start command prompt",   "open_cmd"),
    ("start terminal",         "open_cmd"),
    ("open cmd",               "open_cmd"),
    ("open powershell",        "open_cmd"),
    ("launch powershell",      "open_cmd"),
    ("open console",           "open_cmd"),
    ("open shell",             "open_cmd"),
]