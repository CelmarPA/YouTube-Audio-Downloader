# utils/audio_tags.py

from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.wave import WAVE
from mutagen.id3 import ID3NoHeaderError, TXXX
from mutagen import File


NORMALIZED_TAG = "normalized_lufs"


def is_real_mp3(path: str) -> bool:
    try:
        with open(path, "rb") as f:
            header = f.read(3)
            return header == b"ID3"
    except Exception:
        return False


def mark_as_normalized(path, lufs):
    audio = File(path, easy=True)

    if not audio:
        return

    # WAV → não tem tags confiáveis → marca no info
    if audio.mime and "audio/wav" in audio.mime:
        audio.info.normalized = True
        audio.info.normalized_lufs = lufs
        return

    # MP3
    if audio.mime == ["audio/mpeg"]:
        if audio.tags is None:
            audio.add_tags()

        audio.tags.add(
            TXXX(encoding=3, desc=NORMALIZED_TAG, text=str(lufs))
        )

    else:
        # FLAC / M4A / OGG
        audio[NORMALIZED_TAG] = str(lufs)

    audio.save()


def is_normalized(path):
    print(f"ESTE È O PATHHHHHHHHHHHHHHHHHHHHHHHH: {path}")
    try:
        print("TRY ESTA SENDO CHAMADOOOOOOOOOOOOOOOOOOOOOOOOOO")
        audio = File(path)
        print(
            f"O AUDIOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO È NORMALIZADO: {audio}")
        if audio is None:
            return False

        if audio.mime and "audio/wav" in audio.mime:
            return getattr(audio.info, "normalized", False)

        tags = audio.tags

        if not tags:
            return False

        # MP3 (ID3 → TXXX)
        if audio.mime == ["audio/mpeg"]:
            return f"TXXX:{NORMALIZED_TAG}" in tags

        # FLAC / OGG / M4A
        return NORMALIZED_TAG in tags

    except Exception as e:
        print(f"[is_normalized][ERROR] {path}: {e}")
        return False
