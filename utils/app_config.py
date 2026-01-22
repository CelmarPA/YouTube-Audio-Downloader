# utils/app_config.py
import json
import os
import sys
from typing import Any, Dict


def get_app_data_dir() -> str:
    """
    Returns the path to the application configuration directory.

    - In development: uses a local 'config' folder.
    - In release (PyInstaller): uses %APPDATA%\YouTube Audio Downloader.

    :return: Path to the configuration directory
    :rtype: str
    """
    if getattr(sys, "frozen", False):
        base: str = os.environ.get("APPDATA", os.path.expanduser("~"))
        return os.path.join(base, "YouTube Audio Downloader")
    return os.path.join(os.path.dirname(__file__), "..", "config")


CONFIG_DIR: str = get_app_data_dir()
CONFIG_FILE: str = os.path.join(CONFIG_DIR, "app_config.json")

DEFAULT_CONFIG: Dict[str, Any] = {
    "language": "en-US",
    "theme": "light"
}


def load_config() -> Dict[str, Any]:
    """
    Load the application configuration from disk.

    If the configuration file does not exist, it will be created
    with the default settings.

    :return: Configuration dictionary
    :rtype: dict
    """

    os.makedirs(CONFIG_DIR, exist_ok=True)

    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)

        return DEFAULT_CONFIG.copy()

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(data: Dict[str, Any]) -> None:
    """
    Save the application configuration to disk.

    :param data: Configuration dictionary to save
    :type data: dict
    """

    os.makedirs(CONFIG_DIR, exist_ok=True)

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_state_file() -> str:
    """
    Returns the correct path for the download STATE_FILE depending
    on whether the app is in development or release mode.

    - Development: uses a local 'download_state' folder in project root.
    - Release (PyInstaller): uses %APPDATA%\YouTube Audio Downloader.

    :return: Full path to the state file
    :rtype: str
    """

    if getattr(sys, "frozen", False):
        app_data: str = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "YouTube Audio Downloader")
        os.makedirs(app_data, exist_ok=True)

        return os.path.join(app_data, ".download_state.json")

    else:
        os.makedirs("download_state", exist_ok=True)

        return os.path.join("download_state", ".download_state.json")
