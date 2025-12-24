# utils/paths.py

import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS

    except AttributeError:
        base_path = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    return os.path.join(base_path, relative_path)
