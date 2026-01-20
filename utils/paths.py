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
    Resolve the absolute path to a resource file.
    Supports both development and PyInstaller.
    """
    return os.path.join(_get_base_path(), relative_path)


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
