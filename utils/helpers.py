# utils/helpers.py

import os

from typing import Any

from utils import is_normalized


def safe_float(val: Any, default: float=0.0) -> float:
    """
    Safely convert a value to float.

    If conversion fails, the provided default value is returned.

    :param val: Value to convert
    :type val: any
    :param default: Default value if conversion fails
    :type default: float
    :return: Converted float value or default
    :rtype: float
    """

    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def duration_format(duration_sec: float) -> str:
    """
    Convert seconds to H:MM:SS or M:SS format.

    :param duration_sec: seconds: duration in seconds
    :type duration_sec: float
    :return: formatted duration
    :rtype: str
    """

    if not duration_sec:
        return "--:--"

    if duration_sec >= 3600:
        hours: int = duration_sec // 3600
        minutes: int = (duration_sec % 3600) // 60
        seconds: int = duration_sec % 60

        duration_str: str = f"{hours}:{minutes:02d}:{seconds:02d}"

    else:
        minutes: int = duration_sec // 60
        seconds: int = duration_sec % 60

        duration_str = f"{minutes}:{seconds:02d}"

    return duration_str


def mark_already_downloaded(
    entries: list,
    playlist_dir: str,
    audio_format: str,
    keep_original: bool,
    normalize_audio: bool
) -> None:
    """
    Mark playlist entries as already downloaded.

    The decision takes into account:
    - audio file existence
    - video file existence when keep_original is enabled
    - actual LUFS normalization when normalize_audio is enabled

    :param entries: Playlist entries metadata
    :type entries: list
    :param playlist_dir: Directory where playlist files are stored
    :type playlist_dir: str
    :param audio_format: Target audio format (e.g. mp3, m4a)
    :type audio_format: str
    :param keep_original: Whether original video should exist
    :type keep_original: bool
    :param normalize_audio: Whether LUFS normalization is required
    :type normalize_audio: bool
    """

    if not os.path.isdir(playlist_dir):
        return

    audio_ext: str = f".{audio_format.lower()}"

    for entry in entries:
        entry["_already_downloaded"] = False

        video_id: str = entry.get("id")

        if not video_id:
            continue

        audio_found: bool = False
        video_found: bool = False
        audio_path: str = None


        for root, _, files in os.walk(playlist_dir):
            for file in files:
                if f"[{video_id}]" not in file:
                    continue

                lower: str = file.lower()

                if lower.endswith(audio_ext):
                    audio_found: bool = True
                    audio_path: str = os.path.join(root, file)

                elif lower.endswith(".mp4"):
                    video_found: bool = True

            # 🔍 Search for related files inside playlist directory
            if audio_found and (not keep_original or video_found):
                break

        # =========================
        # Final evaluation rule
        # =========================
        already: bool = False

        if normalize_audio:
            # Must exist audio AND be normalized
            if audio_found and audio_path and is_normalized(audio_path):
                if keep_original:
                    already: bool = video_found
                else:
                    already: bool = True

        else:
            # Normalization disabled
            if keep_original:
                already: bool = audio_found and video_found

            else:
                already: bool = audio_found

        entry["_already_downloaded"] = already
