# widgets/folders.py

import os.path
import subprocess
import sys
import tkinter as tk

from pathlib import Path
from tkinter import filedialog

from ui.dialogs.themed_messagebox import ThemedMessageBox
from i18n.manager import I18nManager
from utils.app_config import load_config, save_config


config: dict = load_config()
language: str = config.get("language", "en-US")

i18n: I18nManager = I18nManager(language=language)


def get_default_downloads() -> str:
    """
    Get the default Downloads directory for the current user.

    :return: Absolute path to the user's Downloads folder
    :rtype: str
    """

    return str(Path.home() / "Downloads")

# Global variable that stores the current download directory
download_dir = config.get("download_dir") or get_default_downloads()


def choose_folder() -> str:
    """
    Open a folder selection dialog and update the download directory.
    Saves the choice in app_config.json.

    :return: Selected or current download directory
    :rtype: str
    """
    global download_dir

    folder: str = filedialog.askdirectory()

    if folder:
        download_dir = folder

        # 🔹 Save in app_config.json
        config["download_dir"] = download_dir
        save_config(config)

    return download_dir


def open_download_folder(parent: tk.Widget, theme: dict, path: str) -> None:
    """
    Open the given folder path in the system's file explorer.

    Supports:
    - Windows native
    - Windows Subsystem for Linux (WSL)
    - macOS
    - Linux (XDG)

    :param parent: Tkinter parent widget used for error dialogs
    :type parent: tk.Widget
    :param theme: Theme configuration for the message box
    :type theme: dict
    :param path: Directory path to open
    :type path: str
    """

    path: str = os.path.abspath(path)

    try:
        if sys.platform.startswith("win"):
            os.startfile(path)

            return

        elif "microsoft" in os.uname().release.lower():
            result = subprocess.run(
                ["wslpath", '-w', path],
                capture_output=True,
                text=True
            )

            win_path: str = result.stdout.strip()

            subprocess.Popen(["explorer.exe", win_path])

            return

        elif sys.platform.startswith("darwin"):
            subprocess.call(["open", path])

            return

        subprocess.call(["xdg-open", path])

    except Exception as e:
        ThemedMessageBox.show_error(
            parent=parent,
            title=i18n.t("error"),
            message=f"{i18n.t('open_folder_error')} \n{str(e)}",
            theme=theme
        )
