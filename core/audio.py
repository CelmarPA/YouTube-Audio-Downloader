# core/audio.py

import os
import subprocess

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
        """
        Initialize the Audio handler.

        :param file_path: Path to the audio file.
        :type file_path: str
        """

        file_path = os.path.abspath(file_path)

        # Validate file existence
        if not os.path.isfile(file_path):
            raise ValueError(f"Invalid audio file: {file_path}")

        self.file_path = file_path
        self.ffmpeg_path = get_ffmpeg_path()

    def normalize(self, target_lufs: float = -14.0):
        """
        Normalize the audio loudness to a target LUFS value using ffmpeg.

        :param target_lufs: Desired loudness in LUFS (recommended -14.0 for streaming).
        :type target_lufs: float
        """

        # Temporary file used during normalization
        tmp_file: str = os.path.abspath(self.file_path + ".normalized.tmp.wav")

        # ffmpeg command for LUFS loudness normalization
        cmd: list[str] = [
            self.ffmpeg_path,
            "-y",  # Overwrite output files without asking
            "-i", self.file_path,
            "-af", f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11",
            tmp_file
        ]

        try:
            # Execute ffmpeg normalization command
            subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Replace original file with normalized output
            os.replace(tmp_file, self.file_path)

        except subprocess.CalledProcessError as e:
            # ffmpeg execution error
            raise RuntimeError(
                f"Error normalizing audio: "
                f"{e.stderr.decode() if e.stderr else str(e)}"
            )

        except Exception as e:
            # Catch-all for unexpected errors
            raise RuntimeError(f"Unexpected error while normalizing audio: {e}")
