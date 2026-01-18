# utils/app_config.py

import json
import os

CONFIG_DIR: str = os.path.join(os.path.dirname(__file__), "..", "config")
CONFIG_FILE: str = os.path.join(CONFIG_DIR, "app_config.json")

DEFAULT_CONFIG: dict = {
    "language": "en-US",
    "theme": "light"
}


def load_config() -> dict:
    os.makedirs(CONFIG_DIR, exist_ok=True)

    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(data: dict) -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)