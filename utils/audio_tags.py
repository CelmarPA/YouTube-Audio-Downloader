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


def get_lufs(path: str) -> float | None:
    if not os.path.exists(path):
        return None

    cmd = [
        "ffmpeg",
        "-i", path,
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
        "-f", "null",
        "-"
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    for line in result.stderr.splitlines():
        if line.strip().startswith("{") and '"input_i"' in line:
            data = json.loads(line)
            return float(data["input_i"])

    return None


def mark_as_normalized(path: str, lufs: float | None = None) -> None:
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
    print("\n========== IS_NORMALIZED ==========")
    print(f"AUDIO PATH: {path}")

    if not os.path.exists(path):
        print("❌ FILE DOES NOT EXIST")
        return False

    ffmpeg = get_ffmpeg_path()
    print(f"FFMPEG PATH: {ffmpeg}")

    if not ffmpeg or not os.path.exists(ffmpeg):
        raise FileNotFoundError("FFmpeg não encontrado")

    cmd = [
        ffmpeg,
        "-hide_banner",
        "-nostats",
        "-i", path,
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
        "-f", "null",
        "-"
    ]

    print("RUNNING FFMPEG COMMAND:")
    print(" ".join(cmd))

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

    stderr = result.stderr

    # extrai JSON do loudnorm
    start = stderr.find("{")
    end = stderr.rfind("}")

    if start == -1 or end == -1:
        raise RuntimeError("Não foi possível extrair loudnorm JSON")

    data = json.loads(stderr[start:end + 1])

    input_lufs = float(data["input_i"])
    print(f"MEASURED LUFS: {input_lufs}")

    normalized = abs(input_lufs - TARGET_LUFS) <= LUFS_TOLERANCE
    print(f"IS NORMALIZED? {normalized}")

    return normalized
