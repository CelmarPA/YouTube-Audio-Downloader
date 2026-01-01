from mutagen import File
from mutagen.id3 import ID3, TXXX
from mutagen.mp4 import MP4
from mutagen.flac import FLAC
from mutagen.oggopus import OggOpus
from mutagen.oggvorbis import OggVorbis
import os

NORMALIZED_TAG = "X-NORMALIZED"
NORMALIZED_VALUE = "true"


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

    except Exception:
        pass


def is_normalized(path: str) -> bool:
    if not path or not os.path.exists(path):
        return False

    ext = os.path.splitext(path)[1].lower()

    try:
        # =========================
        # MP3
        # =========================
        if ext == ".mp3":
            audio = ID3(path)
            for tag in audio.getall("TXXX"):
                if tag.desc == NORMALIZED_TAG and NORMALIZED_VALUE in tag.text[0].lower():
                    return True
            return False

        # =========================
        # MP4 / M4A
        # =========================
        if ext in {".m4a", ".mp4"}:
            audio = MP4(path)
            data = audio.get("----:com.apple.iTunes:NORMALIZED")
            if not data:
                return False
            return NORMALIZED_VALUE in data[0].decode("utf-8").lower()

        # =========================
        # FLAC / OGG / OPUS
        # =========================
        audio = File(path)
        if not audio:
            return False

        value = audio.get("NORMALIZED")
        if not value:
            return False

        if isinstance(value, list):
            value = " ".join(value)

        return NORMALIZED_VALUE in value.lower()

    except Exception:
        return False
