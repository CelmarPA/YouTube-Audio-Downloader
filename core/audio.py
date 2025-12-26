# core/audio.py

import os
import subprocess

from pydub import AudioSegment
from pydub.effects import normalize
from pydub.exceptions import CouldntDecodeError


class Audio:

    def __init__(self, file_path: str):
        if not os.path.isfile(file_path):
            raise ValueError(f"Arquivo inválido: {file_path}")

        self.file_path = file_path

    def normalize(self, target_lufs: float = -14.0):
        """
        Normaliza o áudio para LUFS usando ffmpeg.
        target_lufs: valor desejado em LUFS (recomendado -14.0 para streaming)
        """
        print("NORMALIZANDO AUDIO EXECUTADO............................")
        try:
            # arquivo temporário para saída
            tmp_file = self.file_path + ".normalized.tmp.wav"

            # Comando ffmpeg para normalização LUFS
            cmd = [
                "ffmpeg",
                "-y",  # sobrescrever sem perguntar
                "-i", self.file_path,
                "-af", f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11",
                tmp_file
            ]

            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Substitui o arquivo original pelo normalizado
            os.replace(tmp_file, self.file_path)

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Erro ao normalizar áudio: {e.stderr.decode() if e.stderr else str(e)}")

        except Exception as e:
            raise RuntimeError(f"Erro inesperado ao normalizar áudio: {e}")

