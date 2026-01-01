#utils/audio_normalization.py

import subprocess
import json
import os

TARGET_LUFS = -14.0
TOLERANCE = 0.5  # margem aceitável


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


import subprocess
import json
import os
from utils import get_ffmpeg_path


TARGET_LUFS = -14.0
LUFS_TOLERANCE = 1.0


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