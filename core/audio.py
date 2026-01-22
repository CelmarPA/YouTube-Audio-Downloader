import os
import subprocess
import sys

from utils import get_ffmpeg_path

from pydub import AudioSegment
from pydub.effects import normalize
from pydub.exceptions import CouldntDecodeError

class Audio:
    """
    Audio utility class responsible for audio post-processing operations,
    such as loudness normalization using ffmpeg.
    """

    def __init__(self, file_path: str):
        file_path = os.path.abspath(file_path)
        if not os.path.isfile(file_path):
            raise ValueError(f"Invalid audio file: {file_path}")
        self.file_path = file_path
        self.ffmpeg_path = get_ffmpeg_path()

    def normalize(self, target_lufs: float = -14.0):
        tmp_file: str = os.path.abspath(self.file_path + ".normalized.tmp.wav")
        cmd: list[str] = [
            self.ffmpeg_path,
            "-y",
            "-i", self.file_path,
            "-af", f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11",
            tmp_file
        ]

        try:
            subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0
            )
            os.replace(tmp_file, self.file_path)

        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Error normalizing audio: {e.stderr.decode() if e.stderr else str(e)}"
            )
        except Exception as e:
            raise RuntimeError(f"Unexpected error while normalizing audio: {e}")
