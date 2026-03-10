"""
Command Dataset for Intent Classification
"""

COMMAND_DATASET = [
    # open_browser
    ("open chrome", "open_browser"),
    ("launch chrome", "open_browser"),
    ("start chrome", "open_browser"),
    ("open browser", "open_browser"),
    ("launch browser", "open_browser"),
    ("start browser", "open_browser"),
    ("open google chrome", "open_browser"),
    ("open firefox", "open_browser"),
    ("launch firefox", "open_browser"),
    ("start firefox", "open_browser"),
    ("browse internet", "open_browser"),
    ("open internet browser", "open_browser"),
    ("go to browser", "open_browser"),
    ("open web browser", "open_browser"),
    ("open edge", "open_browser"),

    # open_calculator
    ("open calculator", "open_calculator"),
    ("launch calculator", "open_calculator"),
    ("start calculator", "open_calculator"),
    ("open calc", "open_calculator"),
    ("start calc", "open_calculator"),
    ("launch calc", "open_calculator"),
    ("i need calculator", "open_calculator"),
    ("open the calculator", "open_calculator"),
    ("run calculator", "open_calculator"),
    ("calculator please", "open_calculator"),

    # open_file_explorer
    ("open file explorer", "open_file_explorer"),
    ("launch file explorer", "open_file_explorer"),
    ("open explorer", "open_file_explorer"),
    ("show files", "open_file_explorer"),
    ("open files", "open_file_explorer"),
    ("browse files", "open_file_explorer"),
    ("open my files", "open_file_explorer"),
    ("open folder", "open_file_explorer"),
    ("launch explorer", "open_file_explorer"),
    ("file manager", "open_file_explorer"),
    ("show my documents", "open_file_explorer"),
    ("open documents", "open_file_explorer"),

    # open_notepad
    ("open notepad", "open_notepad"),
    ("launch notepad", "open_notepad"),
    ("start notepad", "open_notepad"),
    ("open text editor", "open_notepad"),
    ("open notes", "open_notepad"),
    ("start text editor", "open_notepad"),
    ("open writing app", "open_notepad"),

    # open_task_manager
    ("open task manager", "open_task_manager"),
    ("launch task manager", "open_task_manager"),
    ("show running processes", "open_task_manager"),
    ("check running apps", "open_task_manager"),
    ("open process manager", "open_task_manager"),
    ("show cpu usage", "open_task_manager"),
    ("open system monitor", "open_task_manager"),

    # close_app
    ("close chrome", "close_app"),
    ("close browser", "close_app"),
    ("close application", "close_app"),
    ("close app", "close_app"),
    ("close notepad", "close_app"),
    ("close calculator", "close_app"),
    ("close window", "close_app"),
    ("close all apps", "close_app"),
    ("exit browser", "close_app"),
    ("exit application", "close_app"),
    ("terminate app", "close_app"),
    ("kill application", "close_app"),

    # shutdown
    ("shutdown system", "shutdown"),
    ("shutdown computer", "shutdown"),
    ("turn off computer", "shutdown"),
    ("power off", "shutdown"),
    ("shut down", "shutdown"),
    ("switch off computer", "shutdown"),
    ("turn off system", "shutdown"),
    ("shutdown the system", "shutdown"),
    ("power down computer", "shutdown"),
    ("switch off system", "shutdown"),

    # restart
    ("restart system", "restart"),
    ("restart computer", "restart"),
    ("reboot system", "restart"),
    ("reboot computer", "restart"),
    ("restart the computer", "restart"),
    ("reboot the system", "restart"),
    ("restart machine", "restart"),
    ("reboot machine", "restart"),
    ("restart now", "restart"),
    ("reboot now", "restart"),

    # volume_up
    ("increase volume", "volume_up"),
    ("volume up", "volume_up"),
    ("turn up volume", "volume_up"),
    ("louder", "volume_up"),
    ("raise volume", "volume_up"),
    ("increase sound", "volume_up"),
    ("make it louder", "volume_up"),

    # volume_down
    ("decrease volume", "volume_down"),
    ("volume down", "volume_down"),
    ("turn down volume", "volume_down"),
    ("quieter", "volume_down"),
    ("lower volume", "volume_down"),
    ("decrease sound", "volume_down"),
    ("make it quieter", "volume_down"),

    # mute
    ("mute", "mute"),
    ("mute volume", "mute"),
    ("mute sound", "mute"),
    ("silence", "mute"),
    ("turn off sound", "mute"),
    ("no sound", "mute"),

    # take_screenshot
    ("take screenshot", "take_screenshot"),
    ("capture screen", "take_screenshot"),
    ("screenshot", "take_screenshot"),
    ("capture screenshot", "take_screenshot"),
    ("take a screenshot", "take_screenshot"),
    ("snap screen", "take_screenshot"),

    # greet / small talk
    ("hello", "greet"),
    ("hi", "greet"),
    ("hey", "greet"),
    ("good morning", "greet"),
    ("good evening", "greet"),
    ("how are you", "greet"),
    ("what can you do", "greet"),
    ("help me", "greet"),
]
