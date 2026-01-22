# utils/ensure_state_folder.py

import os

def ensure_state_folder(state_file: str):
    """
    Ensures that a STATE FILE folder exists.
    """

    folder: str = os.path.dirname(state_file)

    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
