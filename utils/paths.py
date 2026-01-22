# utils/paths.py

import os
import sys


def _get_base_path() -> str:
    """
    Get base path depending on execution context
    (development or PyInstaller frozen app).
    """
    return getattr(
        sys,
        "_MEIPASS",
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )


def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for development and PyInstaller executable.

    :param relative_path: Relative path to the resource.
    :type relative_path: str
    :return: Absolute path to the resource.
    :rtype: str
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path: str = sys._MEIPASS
    except AttributeError:
        # Fallback: use the current directory in development
        base_path: str = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_ffmpeg_path() -> str:
    """
    Return the absolute path to the ffmpeg executable.

    In frozen mode, the path is resolved from the bundled
    application directory. In development mode, it is resolved
    relative to the project root.

    :return: Absolute path to ffmpeg.exe
    :rtype: str
    :raises FileNotFoundError: If ffmpeg.exe is not found
    """

    ffmpeg_path = os.path.join(
        _get_base_path(),
        "bin",
        "ffmpeg.exe"
    )

    if not os.path.isfile(ffmpeg_path):
        raise FileNotFoundError(
            f"ffmpeg.exe not found in: {ffmpeg_path}"
        )

    return ffmpeg_path
