# util/audio_tags.py
import os
import json
import subprocess

from mutagen import File
from mutagen.id3 import ID3, TXXX
from mutagen.mp4 import MP4
from mutagen.flac import FLAC
from mutagen.oggopus import OggOpus
from mutagen.oggvorbis import OggVorbis

from utils.paths import get_ffmpeg_path


NORMALIZED_TAG = "X-NORMALIZED"
NORMALIZED_VALUE = "true"
TARGET_LUFS = -14.0
LUFS_TOLERANCE = 1.0


def mark_as_normalized(path: str, lufs: float | None = None) -> None:
    """
    Mark an audio file as normalized by writing metadata tags.

    The normalization flag is stored using the appropriate
    tag format depending on the audio container type.

    :param path: Path to the audio file
    :type path: str
    :param lufs: Optional LUFS value to store in metadata
    :type lufs: float | None
    :return: None
    """

    if not path or not os.path.exists(path):
        return

    ext = os.path.splitext(path)[1].lower()

    try:
        # =========================
        # MP3 → ID3 TXXX
        # =========================
        if ext == ".mp3":
            audio = ID3(path)
            value = NORMALIZED_VALUE if lufs is None else f"{NORMALIZED_VALUE};lufs={lufs}"
            audio.add(TXXX(encoding=3, desc=NORMALIZED_TAG, text=value))
            audio.save(v2_version=3)
            return

        # =========================
        # MP4 / M4A
        # =========================
        if ext in {".m4a", ".mp4"}:
            audio = MP4(path)
            value = NORMALIZED_VALUE if lufs is None else f"{NORMALIZED_VALUE};lufs={lufs}"
            audio["----:com.apple.iTunes:NORMALIZED"] = [value.encode("utf-8")]
            audio.save()
            return

        # =========================
        # FLAC / OGG / OPUS
        # =========================
        audio = File(path)
        if audio is None:
            return

        value = NORMALIZED_VALUE if lufs is None else f"{NORMALIZED_VALUE};lufs={lufs}"
        audio["NORMALIZED"] = value
        audio.save()

    except Exception as e:
        _e = e
        pass


def is_normalized(path: str) -> bool:
    """
    Check whether an audio file is normalized to the target LUFS level.

    This function measures the audio loudness using FFmpeg and compares
    the result against the configured target LUFS with a tolerance.

    :param path: Path to the audio file
    :type path: str
    :return: True if the audio is within the normalization tolerance
    :rtype: bool
    """

    if not os.path.exists(path):
        return False

    ffmpeg = get_ffmpeg_path()

    if not ffmpeg or not os.path.exists(ffmpeg):
        raise FileNotFoundError("FFmpeg not founded")

    cmd: list = [
        ffmpeg,
        "-hide_banner",
        "-nostats",
        "-i", path,
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
        "-f", "null",
        "-"
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

    stderr = result.stderr

    start = stderr.find("{")
    end = stderr.rfind("}")

    if start == -1 or end == -1:
        raise RuntimeError("Unable to extract loudnorm JSON")

    data = json.loads(stderr[start:end + 1])

    input_lufs = float(data["input_i"])

    normalized = abs(input_lufs - TARGET_LUFS) <= LUFS_TOLERANCE

    return normalized
