# utils/helpers.py

import os

from utils import is_normalized


def safe_float(val, default=0.0):
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
        hours = duration_sec // 3600
        minutes = (duration_sec % 3600) // 60
        seconds = duration_sec % 60

        duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"

    else:
        minutes = duration_sec // 60
        seconds = duration_sec % 60

        duration_str = f"{minutes}:{seconds:02d}"

    return duration_str


def mark_already_downloaded(
    entries,
    playlist_dir,
    audio_format,
    keep_original,
    normalize_audio
):
    """
    Marca entradas da playlist como já baixadas, levando em conta:
    - existência de áudio
    - existência de vídeo (se keep_original)
    - normalização real por LUFS (se normalize_audio)
    """

    if not os.path.isdir(playlist_dir):
        return

    audio_ext = f".{audio_format.lower()}"

    for entry in entries:
        entry["_already_downloaded"] = False

        video_id = entry.get("id")
        if not video_id:
            continue

        audio_found = False
        video_found = False
        audio_path = None

        # 🔍 Procura arquivos do vídeo na pasta da playlist
        for root, _, files in os.walk(playlist_dir):
            for file in files:
                if f"[{video_id}]" not in file:
                    continue

                lower = file.lower()

                if lower.endswith(audio_ext):
                    audio_found = True
                    audio_path = os.path.join(root, file)

                elif lower.endswith(".mp4"):
                    video_found = True

            # ✅ só sai quando tudo necessário foi encontrado
            if audio_found and (not keep_original or video_found):
                break

        # =========================
        # 🔒 REGRA FINAL ÚNICA
        # =========================
        already = False

        if normalize_audio:
            # precisa existir áudio E estar normalizado
            if audio_found and audio_path and is_normalized(audio_path):
                if keep_original:
                    already = video_found
                else:
                    already = True
        else:
            # normalização desligada
            if keep_original:
                already = audio_found and video_found
            else:
                already = audio_found

        entry["_already_downloaded"] = already
