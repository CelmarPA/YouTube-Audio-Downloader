# core/downloader.py
import time
import os
import yt_dlp
import re
import shutil
import threading
import json

from tkinter import messagebox

from utils import get_ffmpeg_path
from core.audio import Audio

YTDLP_INTERMEDIATE_RE = re.compile(
    r"\.f\d+\.(webm|mp4|mkv|m4a|aac|opus)(\.part)?$",
    re.IGNORECASE
)



import re
import unicodedata

import re
import unicodedata

def sanitize_filename(name: str) -> str:
    if not name:
        return "untitled"

    # Remove Unicode / emojis / acentos (igual yt-dlp)
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")

    # Permite exatamente o que restrictfilenames permite
    name = re.sub(r"[^A-Za-z0-9._@-]+", "_", name)

    # Remove underscores duplicados
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
        progress_hook=None,        # progress_hook(percent: float)
        status_hook=None,          # status_hook(text: str)
        file_finished_hook=None,   # file_finished_hook(filepath: str)
        error_hook=None,            # error_hook(message: str)
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

        self.log_hook = log_hook

        self.pause_event = threading.Event()
        self.pause_event.set()  # começa desbloqueado

    def start(self):
        try:
            os.makedirs(self.output_path, exist_ok=True)
            self.files_to_normalize.clear()
            self._build_ydl_opts()

            if self.status_hook:
                self.status_hook("Iniciando download...")

            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)

            if self.allow_playlist and "entries" in info:
                filtered = []

                for entry in info["entries"]:
                    if self._is_cached_final(entry):
                        if self.log_hook:
                            self.log_hook(f"Cache N2: pulando {entry.get('title')}")
                    else:
                        filtered.append(entry)

                info["entries"] = filtered

                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                    ydl.process_ie_result(info, download=True)

            else:
                # 🔥 VÍDEO ÚNICO
                if not self._is_cached_final(info):
                    with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                        ydl.process_ie_result(info, download=True)
                else:
                    if self.log_hook:
                        self.log_hook("Cache N2: arquivo final já existe")
            # ----------------------------
            # Normaliza
            # ----------------------------
            if self.normalize_enabled:
                self._normalize_files()

            if self.status_hook:
                self.status_hook("Concluído ✔")

        except Exception as e:
            if self.error_hook:
                self.error_hook(str(e))

        finally:
            if not self.paused:
                self._cleanup_files()

                if self.cancel_requested and self.normalize_enabled:
                    if self.keep_after_cancel:
                        self._move_playlist_from_tmp()

                self.blocked_files.clear()

                # if self.cancel_requested:
                #     self._cleanup_cancelled_titles()

                self._cleanup_files()
                self._cleanup_tmp_normalize()
                self.clear_state()

    def _get_final_path(self, info_dict):
        """Constrói o caminho do arquivo final baseado no template do yt-dlp"""
        title = sanitize_filename(info_dict.get("title", "untitled"))
        ext = self.audio_format.lower()

        if self.allow_playlist:
            playlist_title = sanitize_filename(info_dict.get("playlist_title", "playlist"))
            filename = os.path.join(self.output_path, playlist_title, f"{title}.{ext}")
        else:
            filename = os.path.join(self.output_path, f"{title}.{ext}")

        filename = os.path.abspath(filename)
        return filename

    # =========================
    # yt-dlp configuration
    # =========================
    def _build_ydl_opts(self):
        """
        Configurações do yt-dlp com nomes de arquivo "safe".
        """
        base_output = self.output_path

        if self.normalize_enabled:
            # Se normalização está ativada, cria pasta temporária
            self.tmp_dir = os.path.join(base_output, "temp_normalize")
            os.makedirs(self.tmp_dir, exist_ok=True)
            output_dir = self.tmp_dir

        else:
            output_dir = base_output

        # Template de saída seguro
        if self.allow_playlist:
            # Para playlists: cria subpasta com título sanitizado da playlist
            outtmpl = os.path.join(output_dir, "%(playlist_title)s/%(title)s.%(ext)s")

        else:
            # Vídeo único: salva direto na pasta base
            outtmpl = os.path.join(output_dir, "%(title)s.%(ext)s")

        # yt-dlp não vai substituir caracteres especiais, então usamos restrictfilenames
        # para evitar problemas com ffmpeg e paths
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
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": self.audio_format,
                    "preferredquality": self.quality
                }
            ],
            "restrictfilenames": True,  # substitui caracteres inválidos automaticamente
            "quiet": False,  # menos logs do yt-dlp
            "no_warnings": False  # Trocar depois
        }

        self.ydl_opts.update({
            "continuedl": True,   # garante resume
            "nopart": False       # mantém .part
        })

    # =========================
    # Hooks
    # =========================
    def _progress_hook(self, d):
        """
        Hook chamado pelo yt-dlp durante o download.
        Captura TODOS os arquivos gerados (principais e intermediários),
        atualiza progresso e gerencia cancelamento.
        """
        # 🔓 se estiver cancelando, nunca fique pausado
        if self.cancel_requested or self.cancel_after_current:
            self.pause_event.set()

        # ⏸️ PAUSE REAL
        self.pause_event.wait()

        status = d.get("status")
        info = d.get("info_dict") or {}

        print(f"[PROGRESS HOOK] Status: {status}")

        # --------------------------------------------------
        # Arquivo principal em uso (muda durante o processo)
        # Ex: .f271.webm → .mp4 → .mp3
        # --------------------------------------------------
        main_file = (
                d.get("filename")
                or info.get("_filename")
        )

        if main_file:
            main_path = os.path.abspath(main_file)
            print(f"[PROGRESS HOOK] Arquivo principal: {main_path}")
            self.generated_files.add(main_path)

        # --------------------------------------------------
        # Arquivos temporários (.part)
        # --------------------------------------------------
        tmp = d.get("tmpfilename")
        if tmp:
            tmp_path = os.path.abspath(tmp)
            print(f"[PROGRESS HOOK] Arquivo temporário: {tmp_path}")
            self.generated_files.add(tmp_path)

        # --------------------------------------------------
        # Formatos separados (video / audio)
        # Ex: .f271.webm, .f251.webm
        # --------------------------------------------------
        for fmt in info.get("requested_formats", []):
            filepath = fmt.get("filepath")
            if filepath:
                fpath = os.path.abspath(filepath)
                print(f"[PROGRESS HOOK] Formato solicitado: {fpath}")
                self.generated_files.add(fpath)

            tmp_fmt = fmt.get("tmpfilepath")
            if tmp_fmt:
                tmp_fpath = os.path.abspath(tmp_fmt)
                print(f"[PROGRESS HOOK] Temp formato: {tmp_fpath}")
                self.generated_files.add(tmp_fpath)

        # --------------------------------------------------
        # Atualiza progresso
        # --------------------------------------------------
        if status == "downloading":
            total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded_bytes = d.get("downloaded_bytes", 0)

            if total_bytes and self.progress_hook:
                percent = downloaded_bytes / total_bytes * 100
                percent = min(max(percent, 0), 100)

                playlist_index = d.get("playlist_index")
                playlist_count = d.get("playlist_count")

                print(
                    f"[PROGRESS HOOK] Progresso: {percent:.2f}% "
                    f"(Item {playlist_index}/{playlist_count})"
                )

                self.progress_hook(percent, playlist_index, playlist_count)

        if self.cancel_requested:
            print("[PROGRESS HOOK] Cancelamento solicitado")
            raise yt_dlp.utils.DownloadCancelled()

        # if self.cancel_after_current and status == "downloading":
        #     playlist_index = info.get("playlist_index") or 1
        #     if playlist_index > 1:
        #         print("[PROGRESS HOOK] Cancelamento solicitado (após item atual)")
        #         raise yt_dlp.utils.DownloadCancelled()

    # =========================
    # Hooks
    # =========================
    def _postprocessor_hook(self, d):
        if d.get("status") != "finished":
            return

        info = d.get("info_dict") or {}

        # Caminho REAL do arquivo final
        real_file = (
                d.get("filepath")
                or d.get("filename")
                or info.get("_filename")
        )

        if real_file:
            real_file = os.path.abspath(real_file)
            self.generated_files.add(real_file)

            # MP4 original (quando keepvideo=True)
            base, _ = os.path.splitext(real_file)
            mp4 = base + ".mp4"
            if os.path.exists(mp4):
                self.generated_files.add(mp4)

        # -------- CANCELAMENTO --------
        if self.cancel_after_current:
            self.cancel_requested = True

            title = info.get("title", "")
            keep = messagebox.askyesno(
                "Cancelar playlist",
                f"Deseja manter este arquivo?\n\n{os.path.basename(real_file)}"
            )

            self.keep_after_cancel = keep

            if not keep and title:
                self.cancelled_titles.add(title)

            self.cancel_after_current = False

    # =========================
    # Normalization
    # =========================
    def _normalize_files(self):
        """
        Normaliza arquivos de áudio para target LUFS (-14 dB) usando tmp_normalize.
        """

        files_to_process = self._collect_files_for_normalize()

        if not files_to_process:
            print("[NORMALIZE] Nenhum arquivo para normalizar.")
            return

        print("Normalize EXECUTADO")
        print(f"Arquivos para normalizar: {files_to_process}")

        # Filtra apenas os arquivos .mp3 para exibir no progresso
        mp3_files = [f for f in files_to_process if f[0].lower().endswith(".mp3")]

        for index, (tmp_file, final_file) in enumerate(files_to_process, start=1):

            if final_file in self.blocked_files:
                print("[NORMALIZE] Arquivo cancelado ignorado:", final_file)
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
                continue

            # Atualiza status apenas se o arquivo for .mp3
            if tmp_file.lower().endswith(".mp3") and self.status_hook:

                mp3_index = mp3_files.index((tmp_file, final_file)) + 1     # posição correta entre MP3s

                self.status_hook(f"Normalizando áudio ({mp3_index}/{len(mp3_files)})")

            try:
                if tmp_file.lower().endswith(f".{self.audio_format.lower()}"):
                    print(f"[NORMALIZE] Normalizando: {tmp_file}")
                    Audio(tmp_file).normalize(target_lufs=-14.0)

                # Garante que a pasta final exista
                os.makedirs(os.path.dirname(final_file), exist_ok=True)
                shutil.move(tmp_file, final_file)
                print(f"[NORMALIZE] Arquivo movido para destino final: {final_file}")

                # Chama os hooks
                if self.file_finished_hook:
                    self.file_finished_hook(final_file)

                if self.log_hook:
                    self.log_hook(f"Arquivo normalizado e salvo em: {final_file}")

            except Exception as e:
                if self.error_hook:
                    self.error_hook(str(e))

        print("[NORMALIZE] Todos os arquivos normalizados e tmp_normalize removida.")
        self.files_to_normalize.clear()

    # =========================
    # Cleanup
    # =========================
    def _cleanup_files(self):


        print("ESTOU SENDO CHAMADOOOOOO")
        """
        Remove arquivos gerados pelo downloader que não são necessários.
        Respeita keep_original_file e normalização.
        """
        allowed_exts = {f".{self.audio_format.lower()}"}

        if self.keep_original_file:
            allowed_exts.add(".mp4")

        for file_path in list(self.generated_files):
            print(f"IMPRIMINDO GENERATEDD AQUII: {self.generated_files}")
            print(f"IMPRIMINDO BLOQUEADOS AQUII: {self.blocked_files}")
            if file_path in self.blocked_files:
                print("ESTOU SENDO CHAMADOOOOOOO ERRADOOOOO 2222222222")
                continue

            if not os.path.exists(file_path):
                print("ESTOU SENDO CHAMADOOOOOOO ERRADOOOOO 33333333333")
                continue

            filename = os.path.basename(file_path)
            ext = os.path.splitext(filename)[1].lower()

            # remove arquivos intermediários do yt-dlp
            print(f"FILENAME IMPRIMIDO AQUII: {filename}")
            if YTDLP_INTERMEDIATE_RE.search(filename):

                try:
                    os.remove(file_path)
                except OSError:
                    pass
                continue

            # remove arquivos não permitidos
            if ext not in allowed_exts:
                try:
                    os.remove(file_path)
                except OSError:
                    pass

        self._delete_cancelled_files()

    def cancel(self):
        # 🔓 garante que não fique travado em pause
        self.pause_event.set()

        if self.allow_playlist:
            self.cancel_after_current = True
        else:
            self.cancel_requested = True

    def cancel_after_current_item(self):
        self.cancel_after_current = True

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

    # -------------------------
    # Deleta arquivos cancelados
    # -------------------------
    def _delete_cancelled_files(self):
        for file_path in list(self.cancelled_files):
            time.sleep(2)
            print("AQUI EU CHEGUEIIIIIIIIIIIIIIIIIII")
            for attempt in range(5):
                if not os.path.exists(file_path):
                    print("BREAKOUUUUUUUUUUUUUUUUUUUUUUUU")
                    break

                try:
                    print("DELETOUUUUUUUUUUUUUUUUUUUUUUUUUUUUU")
                    print(file_path)
                    os.remove(file_path)
                    if self.log_hook:
                        self.log_hook(f"Arquivo deletado: {file_path}")
                    break

                except PermissionError:
                    time.sleep(0.5)  # espera ffmpeg soltar o handle

            else:
                if self.log_hook:
                    self.log_hook(f"Arquivo NÃO pôde ser deletado (em uso): {file_path}")

            self.cancelled_files.remove(file_path)

    def request_cancel(self):
        self.cancel_after_current = True

    def _cleanup_cancelled_titles(self):
        for title in list(self.cancelled_titles):

            base = sanitize_filename(title)

            for root, _, files in os.walk(self.output_path):
                for f in files:
                    if base in f:
                        try:
                            path = os.path.join(root, f)
                            os.remove(path)

                            if self.log_hook:
                                self.log_hook(f"Arquivo deletado (cancelado): {path}")

                        except Exception as e:
                            print("Falha ao deletar:", e)

            self.cancelled_titles.remove(title)

    def _cleanup_tmp_normalize(self):
        if self.tmp_dir and os.path.exists(self.tmp_dir):
            try:
                shutil.rmtree(self.tmp_dir)
                print(f"[CLEANUP] temp_normalize removida: {self.tmp_dir}")
            except Exception as e:
                print("[CLEANUP] Falha ao remover temp_normalize:", e)

    def _move_playlist_from_tmp(self):
        if not self.tmp_dir or not os.path.exists(self.tmp_dir):
            return

        for name in os.listdir(self.tmp_dir):
            src = os.path.join(self.tmp_dir, name)
            dst = os.path.join(self.output_path, name)

            if os.path.isdir(src):
                # evita sobrescrever pasta existente
                if os.path.exists(dst):
                    continue

                shutil.move(src, dst)
                print(f"[CLEANUP] Playlist movida: {src} → {dst}")

    def _is_cached_final(self, info_dict) -> bool:
        """
        Retorna True se o arquivo FINAL já existe.
        Cache de nível 2.
        """

        final_path = self._get_final_path(info_dict)

        return bool(final_path and os.path.exists(final_path))

    def pause(self):
        self.paused = True
        self._save_state(paused=True)

        if self.status_hook:
            self.status_hook("⏸️ Pausado")
        if self.log_hook:
            self.log_hook("⏸️ Download pausado")

        self.pause_event.clear()

    def resume(self):
        self.paused = False
        self.clear_state()

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

    def clear_state(self):
        if os.path.exists(self.STATE_FILE):
            os.remove(self.STATE_FILE)