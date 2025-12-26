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


def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS

    else:
        base_path = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

    return os.path.join(base_path, 'bin')
