# core/downloader.py
import time
import os
import yt_dlp
import re
import shutil
import threading
import json
import unicodedata

from tkinter import messagebox
from utils import get_ffmpeg_path
from core.audio import Audio

YTDLP_INTERMEDIATE_RE = re.compile(
    r"\.f\d+\.(webm|mp4|mkv|m4a|aac|opus)(\.part)?$",
    re.IGNORECASE
)


def sanitize_filename(name: str) -> str:
    if not name:
        return "untitled"
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    name = re.sub(r"[^A-Za-z0-9._@-]+", "_", name)
    name = re.sub(r"_+", "_", name)
    return name.strip("_")


class Downloader:
    def __init__(
        self,
        url: str,
        output_path: str,
        audio_format: str,
        quality: str,
        allow_playlist: bool,
        keep_original_file: bool,
        normalize_enabled: bool,
        progress_hook=None,
        status_hook=None,
        file_finished_hook=None,
        error_hook=None,
        log_hook=None,
        state_file=None,
    ):
        self.url = url
        self.output_path = output_path
        self.audio_format = audio_format
        self.quality = quality
        self.allow_playlist = allow_playlist
        self.keep_original_file = keep_original_file
        self.normalize_enabled = normalize_enabled

        self.progress_hook = progress_hook
        self.status_hook = status_hook
        self.file_finished_hook = file_finished_hook
        self.error_hook = error_hook
        self.log_hook = log_hook

        self.ffmpeg_path = get_ffmpeg_path()
        self.generated_files = set()
        self.cancelled_files = set()
        self.files_to_normalize = []
        self.collected_files = []
        self.tmp_dir = None
        self.playlist_index = None
        self.playlist_count = None
        self.cancelled = False
        self.keep_after_cancel = False
        self.cancel_requested = False
        self.cancel_after_current = False
        self.blocked_files = set()
        self.cancelled_titles = set()
        self.STATE_FILE = state_file or os.path.join(self.output_path, ".download_state.json")
        self.paused = False
        self.pause_event = threading.Event()
        self.pause_event.set()  # desbloqueado

        self._download_active = False  # indica se download está ativo

    def start(self):
        self._download_active = True
        try:
            os.makedirs(self.output_path, exist_ok=True)
            self.files_to_normalize.clear()
            self._build_ydl_opts()

            if self.status_hook:
                self.status_hook("Iniciando download...")
            if self.log_hook:
                self.log_hook("[START] Iniciando download...")

            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)

            if self.allow_playlist and "entries" in info:
                filtered = []
                for entry in info["entries"]:
                    if self._is_cached_final(entry):
                        if self.log_hook:
                            self.log_hook(f"[CACHE] Pulando (arquivo final já existe): {entry.get('title')}")
                    else:
                        filtered.append(entry)
                info["entries"] = filtered

                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                    ydl.process_ie_result(info, download=True)
            else:
                if not self._is_cached_final(info):
                    with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                        ydl.process_ie_result(info, download=True)
                else:
                    if self.log_hook:
                        self.log_hook("[CACHE] Arquivo final já existe, pulando download")

            if self.normalize_enabled:
                self._normalize_files()

            if self.status_hook:
                self.status_hook("Concluído ✔")
            if self.log_hook:
                self.log_hook("[DONE] Download concluído")

        except Exception as e:
            if self.error_hook:
                self.error_hook(str(e))
            if self.log_hook:
                self.log_hook(f"[ERROR] {e}")

        finally:
            if not self.paused:
                self._cleanup_files()
                if self.cancel_requested and self.normalize_enabled and self.keep_after_cancel:
                    self._move_playlist_from_tmp()
                self.blocked_files.clear()
                self._cleanup_tmp_normalize()
                self._clear_state()
                self._download_active = False

    def _get_final_path(self, info_dict):
        title = sanitize_filename(info_dict.get("title", "untitled"))
        ext = self.audio_format.lower()
        if self.allow_playlist:
            playlist_title = sanitize_filename(info_dict.get("playlist_title", "playlist"))
            filename = os.path.join(self.output_path, playlist_title, f"{title}.{ext}")
        else:
            filename = os.path.join(self.output_path, f"{title}.{ext}")
        return os.path.abspath(filename)

    def _build_ydl_opts(self):
        base_output = self.output_path
        if self.normalize_enabled:
            self.tmp_dir = os.path.join(base_output, "temp_normalize")
            os.makedirs(self.tmp_dir, exist_ok=True)
            output_dir = self.tmp_dir
        else:
            output_dir = base_output

        if self.allow_playlist:
            outtmpl = os.path.join(output_dir, "%(playlist_title)s/%(title)s.%(ext)s")
        else:
            outtmpl = os.path.join(output_dir, "%(title)s.%(ext)s")

        self.ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "ffmpeg_location": self.ffmpeg_path,
            "outtmpl": outtmpl,
            "noplaylist": not self.allow_playlist,
            "merge_output_format": "mp4",
            "external_downloader_args": ["-nostdin"],
            "keepvideo": self.keep_original_file,
            "progress_hooks": [self._progress_hook],
            "postprocessor_hooks": [self._postprocessor_hook],
            "postprocessors": [
                {"key": "FFmpegExtractAudio", "preferredcodec": self.audio_format, "preferredquality": self.quality}
            ],
            "restrictfilenames": True,
            "quiet": False,
            "no_warnings": False,
            "continuedl": True,
            "nopart": False
        }

    def _progress_hook(self, d):
        if self.cancel_requested or self.cancel_after_current:
            self.pause_event.set()
        self.pause_event.wait()

        status = d.get("status")
        info = d.get("info_dict") or {}

        if status == "downloading":
            downloaded_bytes = d.get("downloaded_bytes", 0)
            total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate") or 1
            percent = downloaded_bytes / total_bytes * 100
            speed = d.get("speed") or 0
            eta = d.get("eta") or 0
            downloaded_mb = downloaded_bytes / (1024 * 1024)
            total_mb = total_bytes / (1024 * 1024)
            playlist_index = d.get("playlist_index")
            playlist_count = d.get("playlist_count")

            status_text = f"{percent:.1f}% — {downloaded_mb:.2f}/{total_mb:.2f} MB — {speed / 1024:.2f} KB/s — ETA {eta}s"
            if playlist_index and playlist_count:
                status_text = f"Item {playlist_index}/{playlist_count} — {status_text}"

            # Adiciona arquivo temporário (.part ou intermediário) à lista de gerados
            tmp_file = d.get("tmpfilename")
            if tmp_file:
                self.generated_files.add(os.path.abspath(tmp_file))

            if downloaded_bytes == 0 and self.log_hook:
                self.log_hook(f"[DOWNLOAD] Iniciando download: {info.get('title', 'untitled')}")

            if self.log_hook:
                self.log_hook(f"[DOWNLOAD] {status_text}")

            if self.progress_hook:
                self.progress_hook(percent, playlist_index, playlist_count, status_text)

    def _postprocessor_hook(self, d):
        if d.get("status") != "finished":
            return

        info = d.get("info_dict") or {}

        # Caminho do arquivo final ou intermediário
        paths_to_add = set()

        # Adiciona caminho principal (final ou intermediário)
        main_file = d.get("filepath") or d.get("filename") or info.get("_filename")
        if main_file:
            main_file = os.path.abspath(main_file)
            paths_to_add.add(main_file)

            # Se keepvideo=True, garante mp4 original
            base, _ = os.path.splitext(main_file)
            mp4 = base + ".mp4"
            if os.path.exists(mp4):
                paths_to_add.add(mp4)

        # Adiciona arquivos intermediários do yt-dlp se existirem
        out_dir = os.path.dirname(main_file) if main_file else self.output_path
        basename = os.path.splitext(os.path.basename(main_file or "temp"))[0]

        for f in os.listdir(out_dir):
            if f.startswith(basename) and YTDLP_INTERMEDIATE_RE.search(f):
                paths_to_add.add(os.path.join(out_dir, f))

        # Adiciona todos os encontrados em generated_files
        for path in paths_to_add:
            self.generated_files.add(path)
            if self.log_hook:
                self.log_hook(f"[POSTPROCESS] Arquivo rastreado: {path}")

        # Hook externo
        if main_file and self.file_finished_hook:
            self.file_finished_hook(main_file)

        # -------- CANCELAMENTO --------
        if self.cancel_after_current:
            self.cancel_requested = True
            title = info.get("title", "")
            keep = messagebox.askyesno(
                "Cancelar playlist",
                f"Deseja manter este arquivo?\n\n{os.path.basename(main_file)}"
            )
            self.keep_after_cancel = keep

            if not keep and title:
                self.cancelled_titles.add(title)

            if self.log_hook:
                self.log_hook(f"[CANCEL] Cancelamento solicitado — manter arquivo? {keep}")

            self.cancel_after_current = False

    def _normalize_files(self):
        """
        Normaliza arquivos de áudio para target LUFS (-14 dB) usando tmp_normalize.
        """

        files_to_process = self._collect_files_for_normalize()

        total_files = len(files_to_process)
        if total_files == 0:
            if self.log_hook:
                self.log_hook("[NORMALIZE] Nenhum arquivo para normalizar.")
            return

        if self.log_hook:
            self.log_hook(f"[NORMALIZE] {total_files} arquivo(s) serão normalizados")

        for index, (tmp_file, final_file) in enumerate(files_to_process, start=1):
            if final_file in self.blocked_files:
                if self.log_hook:
                    self.log_hook(f"[NORMALIZE] Arquivo cancelado, ignorando: {final_file}")
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
                continue

            # Log do arquivo atual
            if self.log_hook:
                self.log_hook(f"[NORMALIZE] ({index}/{total_files}) Normalizando: {tmp_file}")

            try:
                # Normaliza apenas o arquivo no formato de áudio escolhido
                if tmp_file.lower().endswith(f".{self.audio_format.lower()}"):
                    Audio(tmp_file).normalize(target_lufs=-14.0)

                # Garante que a pasta final exista e move o arquivo
                os.makedirs(os.path.dirname(final_file), exist_ok=True)
                shutil.move(tmp_file, final_file)

                # Log sucesso
                if self.log_hook:
                    self.log_hook(f"[NORMALIZE] ({index}/{total_files}) Normalizado e movido para: {final_file}")

                # Hook de arquivo finalizado
                if self.file_finished_hook:
                    self.file_finished_hook(final_file)

            except Exception as e:
                if self.error_hook:
                    self.error_hook(f"[NORMALIZE][ERROR] Falha ao normalizar {tmp_file}: {e}")

        if self.log_hook:
            self.log_hook(f"[NORMALIZE] Todos os {total_files} arquivos processados")

    def _cleanup_files(self):
        allowed_exts = {f".{self.audio_format.lower()}"}
        if self.keep_original_file:
            allowed_exts.add(".mp4")

        for file_path in list(self.generated_files):
            if file_path in self.blocked_files or not os.path.exists(file_path):
                continue

            filename = os.path.basename(file_path)
            ext = os.path.splitext(filename)[1].lower()

            if YTDLP_INTERMEDIATE_RE.search(filename):
                try:
                    os.remove(file_path)
                    if self.log_hook:
                        self.log_hook(f"[CLEANUP] Arquivo intermediário removido: {file_path}")
                except OSError as e:
                    if self.log_hook:
                        self.log_hook(f"[ERROR] Falha ao remover arquivo intermediário: {file_path} — {e}")
                continue

            if ext not in allowed_exts:
                try:
                    os.remove(file_path)
                    if self.log_hook:
                        self.log_hook(f"[CLEANUP] Arquivo removido (ext não permitido): {file_path}")
                except OSError as e:
                    if self.log_hook:
                        self.log_hook(f"[ERROR] Falha ao remover arquivo: {file_path} — {e}")

        self._delete_cancelled_files()

    def _delete_cancelled_files(self):
        for file_path in list(self.cancelled_files):
            time.sleep(2)
            for attempt in range(5):
                if not os.path.exists(file_path):
                    break
                try:
                    os.remove(file_path)
                    if self.log_hook:
                        self.log_hook(f"[CANCEL] Arquivo deletado: {file_path}")
                    break
                except PermissionError:
                    time.sleep(0.5)
            else:
                if self.log_hook:
                    self.log_hook(f"[CANCEL] Arquivo NÃO pôde ser deletado (em uso): {file_path}")
            self.cancelled_files.remove(file_path)

    def _cleanup_tmp_normalize(self):
        if self.tmp_dir and os.path.exists(self.tmp_dir):
            try:
                shutil.rmtree(self.tmp_dir)
                if self.log_hook:
                    self.log_hook(f"[CLEANUP] temp_normalize removida: {self.tmp_dir}")
            except Exception as e:
                if self.log_hook:
                    self.log_hook(f"[ERROR] Falha ao remover temp_normalize: {e}")

    def _move_playlist_from_tmp(self):
        if not self.tmp_dir or not os.path.exists(self.tmp_dir):
            return
        for name in os.listdir(self.tmp_dir):
            src = os.path.join(self.tmp_dir, name)
            dst = os.path.join(self.output_path, name)
            if os.path.isdir(src) and not os.path.exists(dst):
                shutil.move(src, dst)
                if self.log_hook:
                    self.log_hook(f"[CLEANUP] Playlist movida: {src} → {dst}")

    def _is_cached_final(self, info_dict) -> bool:
        final_path = self._get_final_path(info_dict)
        return bool(final_path and os.path.exists(final_path))

    def pause(self):
        if not self._download_active:
            return  # não pausa se nada está ativo

        self.paused = True
        if self._download_active:
            self._save_state(paused=True)
        if self.status_hook:
            self.status_hook("⏸️ Pausado")
        if self.log_hook:
            self.log_hook("⏸️ Download pausado")
        self.pause_event.clear()

    def resume(self):
        self.paused = False
        self._clear_state()
        if self.status_hook:
            self.status_hook("▶️ Retomando download...")
        if self.log_hook:
            self.log_hook("▶️ Download retomado")
        self.pause_event.set()

    def _save_state(self, paused=False):
        state = {
            "url": self.url,
            "output_path": self.output_path,
            "audio_format": self.audio_format,
            "quality": self.quality,
            "allow_playlist": self.allow_playlist,
            "keep_original": self.keep_original_file,
            "normalize_enabled": self.normalize_enabled,
            "paused": paused
        }
        with open(self.STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        if self.log_hook:
            self.log_hook(f"[STATE] Estado salvo (paused={paused}): {self.STATE_FILE}")

    def _clear_state(self):
        if os.path.exists(self.STATE_FILE):
            os.remove(self.STATE_FILE)
            if self.log_hook:
                self.log_hook(f"[STATE] Arquivo de estado removido: {self.STATE_FILE}")

    def save_state_on_close(self):
        """
        Deve ser chamado quando a janela é fechada.
        Salva apenas se houver download ativo ou pausado.
        """
        if self._download_active or self.paused:
            self._save_state(paused=self.paused)


    def _collect_files_for_normalize(self):
        """
        Coleta arquivos na pasta tmp_normalize que devem ser normalizados.
        Retorna uma lista de tuplas (tmp_file, final_file).
        """

        if not os.path.exists(self.tmp_dir):
            return []

        files_to_process = []

        for root, _, files in os.walk(self.tmp_dir):
            for f in files:
                print("OS ARQUIVOS SAO:", f)
                ext = os.path.splitext(f)[1].lower()

                # Coleta apenas arquivos de áudio no formato escolhido
                if ext not in [".mp3", ".mp4"]:
                    continue

                tmp_file = os.path.join(root, f)

                if self.allow_playlist:
                    relative_path = os.path.relpath(tmp_file, self.tmp_dir)
                    final_file = os.path.join(self.output_path, relative_path)

                else:
                    final_file = os.path.join(self.output_path, f)

                files_to_process.append((tmp_file, final_file))

        print("ESSESS SAO OS PARA PROCESSAR:", files_to_process)
        return files_to_process
