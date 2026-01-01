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
from utils.audio_tags import mark_as_normalized, is_normalized
from utils import is_normalized

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
        self.tmp_playlist_dir = None
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
        self.selected_entries = None

        self._download_active = False  # indica se download está ativo
        self.playlist_dir = None

    def start(self):
        self._download_active = True
        self.tmp_playlist_dir = None

        try:
            # =============================
            # 1️⃣ Inicialização
            # =============================
            os.makedirs(self.output_path, exist_ok=True)

            self.generated_files.clear()
            self.cancelled_files.clear()
            self.collected_files.clear()
            self.files_to_normalize.clear()

            if self.status_hook:
                self.status_hook("Iniciando download...")

            if self.log_hook:
                self.log_hook("[START] Iniciando download")

            # =============================
            # 2️⃣ Extrai info SEM baixar
            # =============================
            self._build_ydl_opts()  # ✅ GARANTE ydl_opts

            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)

            # =============================
            # 3️⃣ PLAYLIST (COM TMP)
            # =============================
            if self.allow_playlist and "entries" in info:
                playlist_name = sanitize_filename(info.get("title", "Playlist"))
                self.playlist_dir = os.path.join(self.output_path, playlist_name)

                # 🔥 TMP EXCLUSIVO DA PLAYLIST
                self.tmp_playlist_dir = os.path.join(
                    self.output_path,
                    f".tmp_playlist_{playlist_name}_{int(time.time())}"
                )
                os.makedirs(self.tmp_playlist_dir, exist_ok=True)

                # 🔥 build ydl_opts APONTANDO PARA TMP DA PLAYLIST
                self._build_ydl_opts()
                self.ydl_opts["outtmpl"] = os.path.join(
                    self.tmp_playlist_dir,
                    "%(title)s [%(id)s].%(ext)s"
                )

                selected_ids = None
                if self.selected_entries:
                    selected_ids = {e["id"] for e in self.selected_entries if e.get("id")}

                filtered_entries = []

                for entry in info.get("entries", []):
                    if not entry:
                        continue

                    video_id = entry.get("id")
                    if not video_id:
                        continue

                    if selected_ids and video_id not in selected_ids:
                        continue

                    title = sanitize_filename(entry.get("title", "untitled"))
                    final_base = os.path.join(
                        self.playlist_dir,
                        f"{title} [{video_id}]"
                    )

                    if self._should_download(final_base):
                        filtered_entries.append(entry)
                    else:
                        if self.log_hook:
                            self.log_hook(f"[CACHE] Pulando: {title}")

                if not filtered_entries:
                    if self.log_hook:
                        self.log_hook("[CACHE] Nenhum item novo para baixar")
                    shutil.rmtree(self.tmp_playlist_dir, ignore_errors=True)
                    return

                info["entries"] = filtered_entries

                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                    ydl.process_ie_result(info, download=True)

            # =============================
            # 4️⃣ SINGLE (SEM TMP)
            # =============================
            else:
                self._build_ydl_opts()

                video_id = info.get("id")
                title = sanitize_filename(info.get("title", "untitled"))

                if video_id:
                    base_path = os.path.join(
                        self.output_path,
                        f"{title} [{video_id}]"
                    )
                    if not self._should_download(base_path):
                        if self.log_hook:
                            self.log_hook("[CACHE] Arquivo já existe, pulando")
                        return

                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                    ydl.process_ie_result(info, download=True)

            # =============================
            # 5️⃣ FINAL OK
            # =============================
            if self.status_hook:
                self.status_hook("Download concluído ✔")

            if self.log_hook:
                self.log_hook("[DONE] Download concluído")

        except Exception as e:
            if self.error_hook:
                self.error_hook(str(e))
            if self.log_hook:
                self.log_hook(f"[ERROR] {e}")

        finally:
            # =============================
            # 6️⃣ CANCELADO + MANTER
            # =============================
            if self.cancel_requested and self.keep_after_cancel:
                if self.log_hook:
                    self.log_hook("[CANCEL] Cancelado com manter")

                if self.normalize_enabled:
                    self._normalize_files()
                    self._cleanup_files()

                # 🔥 move TMP → pasta final
                if self.tmp_playlist_dir and os.path.exists(self.tmp_playlist_dir):
                    os.makedirs(self.playlist_dir, exist_ok=True)
                    for f in os.listdir(self.tmp_playlist_dir):
                        shutil.move(
                            os.path.join(self.tmp_playlist_dir, f),
                            os.path.join(self.playlist_dir, f)
                        )
                    shutil.rmtree(self.tmp_playlist_dir, ignore_errors=True)

                self._cleanup_tmp_normalize()
                self._clear_state()
                self._download_active = False
                return

            # =============================
            # 7️⃣ CANCELADO SEM MANTER
            # =============================
            if self.cancel_requested and not self.keep_after_cancel:
                if self.log_hook:
                    self.log_hook("[CANCEL] Cancelado sem manter")

                # 🔥 APAGA SOMENTE A TMP
                if self.tmp_playlist_dir:
                    shutil.rmtree(self.tmp_playlist_dir, ignore_errors=True)

                self._cleanup_files()
                self._cleanup_tmp_normalize()
                self._clear_state()
                self._download_active = False
                return

            # =============================
            # 8️⃣ FLUXO NORMAL
            # =============================
            if not self.paused:
                if self.normalize_enabled:
                    self._normalize_files()

                # 🔥 LIMPA INTERMEDIÁRIOS AQUI
                self._cleanup_files()

                # 🔥 move TMP → pasta final
                if self.tmp_playlist_dir and os.path.exists(self.tmp_playlist_dir):
                    os.makedirs(self.playlist_dir, exist_ok=True)
                    for f in os.listdir(self.tmp_playlist_dir):
                        shutil.move(
                            os.path.join(self.tmp_playlist_dir, f),
                            os.path.join(self.playlist_dir, f)
                        )
                    shutil.rmtree(self.tmp_playlist_dir, ignore_errors=True)

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

        # ===============================
        # 🔹 NORMALIZE TEM PRIORIDADE ABSOLUTA
        # ===============================
        if self.normalize_enabled:
            self.tmp_dir = os.path.join(base_output, "temp_normalize")
            os.makedirs(self.tmp_dir, exist_ok=True)
            output_dir = self.tmp_dir

        # ===============================
        # 🔹 SEM NORMALIZE → pode usar temp de playlist
        # ===============================
        elif self.allow_playlist and self.tmp_playlist_dir:
            output_dir = self.tmp_playlist_dir

        # ===============================
        # 🔹 SEM NORMALIZE E SEM PLAYLIST
        # ===============================
        else:
            output_dir = base_output

        self.ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "ffmpeg_location": self.ffmpeg_path,

            # 🔥 SEMPRE um único template
            "outtmpl": os.path.join(
                output_dir,
                "%(title)s [%(id)s].%(ext)s"
            ),

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
                    "preferredquality": self.quality,
                }
            ],

            "restrictfilenames": True,
            "continuedl": True,
            "nopart": False,
        }

    # ================== Método cancel ==================
    def cancel(self, after_current=False):
        """
        Cancela o download.
        :param after_current: se True, cancela apenas após o item atual (playlist)
        """
        self.pause_event.set()

        if after_current and self.allow_playlist:
            self.cancel_after_current = True
            if self.log_hook:
                self.log_hook("⏭️ Cancelamento solicitado (aguardando item atual terminar)")
        else:
            self.cancel_requested = True
            self.cancel_after_current = False
            if self.log_hook:
                self.log_hook("[CANCEL] Cancelamento imediato solicitado")

    # ================== Progress hook ==================
    def _progress_hook(self, d):
        self.pause_event.wait()

        # captura arquivos TEMPORÁRIOS do yt-dlp
        for key in ("tmpfilename", "filename"):
            path = d.get(key)
            if path:
                self.generated_files.add(os.path.abspath(path))

        # Cancelamento imediato
        if self.cancel_requested and not self.cancel_after_current:
            tmp_file = d.get("tmpfilename")
            if tmp_file and os.path.exists(tmp_file):
                try:
                    os.remove(tmp_file)
                    if self.log_hook:
                        self.log_hook(f"[CANCEL] Arquivo temporário removido: {tmp_file}")
                except Exception as e:
                    if self.log_hook:
                        self.log_hook(f"[ERROR] Falha ao remover temp cancelado: {tmp_file} — {e}")

            raise yt_dlp.utils.DownloadError("Download cancelado pelo usuário")

    # ================== Postprocessor hook ==================
    def _postprocessor_hook(self, d):
        if d.get("status") != "finished":
            return

        info = d.get("info_dict") or {}

        # 🔥 captura ABSOLUTAMENTE tudo que o ffmpeg gerar
        possible_paths = []

        for key in (
                "filepath",
                "filename",
                "_filename",
        ):
            val = d.get(key) or info.get(key)
            if isinstance(val, str):
                possible_paths.append(val)

        # casos onde o yt-dlp devolve lista
        requested = d.get("requested_downloads")
        if isinstance(requested, list):
            for item in requested:
                path = item.get("filepath") or item.get("filename")
                if path:
                    possible_paths.append(path)

        # registra tudo
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            self.generated_files.add(abs_path)

        # -------- lógica de cancelamento após item --------
        if self.cancel_after_current:
            self.cancel_after_current = False

            keep = True
            main_file = possible_paths[-1] if possible_paths else None

            if main_file and os.path.exists(main_file):
                keep = messagebox.askyesno(
                    "Cancelar playlist",
                    f"Deseja manter o(s) arquivo(s) baixado(s)?\n\n{os.path.basename(main_file)}"
                )
                if not keep:
                    self.cancelled_files.add(os.path.abspath(main_file))

            self.keep_after_cancel = keep
            self.cancel_requested = True

            if self.log_hook:
                self.log_hook(f"[CANCEL] Playlist cancelada — manter arquivo atual? {keep}")

    def _normalize_files(self):
        """
        Normaliza arquivos de áudio para target LUFS (-14 dB)
        SOMENTE arquivos gerados no tmp_normalize.
        """

        files_to_process = self._collect_files_for_normalize()
        tmp_dir = self.tmp_dir

        # 🔥 CANCELADO + MANTER → apenas mover arquivos, sem normalizar
        if self.cancel_requested and self.keep_after_cancel:
            if self.log_hook:
                self.log_hook("[NORMALIZE] Cancelado com manter → pulando normalização")

            for tmp_file, final_file in files_to_process:
                if not tmp_file or not final_file:
                    continue

                if not os.path.exists(tmp_file):
                    continue

                os.makedirs(os.path.dirname(final_file), exist_ok=True)
                try:
                    shutil.move(tmp_file, final_file)
                    if self.file_finished_hook:
                        self.file_finished_hook(final_file)
                except Exception:
                    pass

            return

        print(f"OS ARQUIVOS PARA PROCESSARRRRRRRRRRRRR {files_to_process}")

        if not tmp_dir:
            return

        if self.log_hook:
            self.log_hook(f"[NORMALIZE] Arquivos coletados: {len(files_to_process)}")

        if not files_to_process:
            if self.log_hook:
                self.log_hook("[NORMALIZE] Nenhum arquivo para normalizar.")
            return

        for index, (tmp_file, final_file) in enumerate(files_to_process, start=1):
            if not tmp_file or not final_file:
                continue

            tmp_file = os.path.abspath(tmp_file)
            final_file = os.path.abspath(final_file)

            # ❌ arquivo não existe
            if not os.path.exists(tmp_file):
                if self.log_hook:
                    self.log_hook(f"[NORMALIZE] Arquivo não encontrado: {tmp_file}")
                continue

            # ❌ arquivo cancelado
            if final_file in self.cancelled_files:
                if self.log_hook:
                    self.log_hook(f"[NORMALIZE] Ignorado (cancelado): {tmp_file}")
                continue

            # ❌ pasta ou arquivo bloqueado
            if any(final_file.startswith(os.path.abspath(b)) for b in self.blocked_files):
                if self.log_hook:
                    self.log_hook(f"[NORMALIZE] Ignorado (bloqueado): {final_file}")
                try:
                    os.remove(tmp_file)
                except OSError:
                    pass
                continue

            # ❌ extensão errada (normaliza SOMENTE o formato final)
            if not tmp_file.lower().endswith(f".{self.audio_format.lower()}"):
                if self.log_hook:
                    self.log_hook(f"[NORMALIZE] Ignorado (extensão): {tmp_file}")

                shutil.move(tmp_file, final_file)
                continue

            if is_normalized(final_file):
                if self.log_hook:
                    self.log_hook(f"[NORMALIZE] Ignorado (já normalizado): {final_file}")

                continue

            if self.log_hook:
                self.log_hook(
                    f"[NORMALIZE] ({index}/{len(files_to_process)}) Normalizando: {os.path.basename(tmp_file)}"
                )

            try:
                print(f"ESTE È O TEMP FILE: {tmp_file}")
                print(f"ESTE È O TEMP final FILE: {final_file}")
                # 🎧 NORMALIZA
                Audio(tmp_file).normalize(target_lufs=-14.0)

                # 📁 garante pasta final
                os.makedirs(os.path.dirname(final_file), exist_ok=True)
                print(f"ESTE E O TEMPPPPPP FILE: {tmp_file}")

                print(f"ESTE E O FINALLLLL FILE: {final_file}")
                # 🚚 move para destino final
                shutil.move(tmp_file, final_file)

                self.generated_files.add(os.path.abspath(final_file))
                self.collected_files.append(os.path.abspath(final_file))

                mark_as_normalized(final_file, -14.0)

                if self.log_hook:
                    self.log_hook(f"[NORMALIZE] OK → {final_file}")

                if self.file_finished_hook:
                    self.file_finished_hook(final_file)

            except Exception as e:
                if self.error_hook:
                    self.error_hook(f"[NORMALIZE][ERROR] {tmp_file}: {e}")
                    print(f"[NORMALIZE][ERROR] {tmp_file}: {e}")

        if self.log_hook:
            self.log_hook("[NORMALIZE] Finalizado")

    def _cleanup_files(self):
        """
        Remove apenas arquivos gerados nesta execução.
        NUNCA remove pastas inteiras de playlist.
        """

        allowed_exts = {f".{self.audio_format.lower()}"}

        if self.keep_original_file:
            allowed_exts.add(".mp4")

        # 1️⃣ Remove arquivos explicitamente cancelados
        self._delete_cancelled_files()

        # 2️⃣ Remove arquivos intermediários e não permitidos
        for file_path in list(self.generated_files):
            if file_path in self.blocked_files or not os.path.exists(file_path):
                continue

            filename = os.path.basename(file_path)
            ext = os.path.splitext(filename)[1].lower()

            # 🔥 SEMPRE remover intermediários do yt-dlp
            if YTDLP_INTERMEDIATE_RE.search(filename):
                try:
                    os.remove(file_path)
                    if self.log_hook:
                        self.log_hook(f"[CLEANUP] Intermediário removido: {file_path}")
                except OSError as e:
                    if self.log_hook:
                        self.log_hook(f"[ERROR] Falha ao remover intermediário: {file_path} — {e}")
                continue

            # 🔥 Remove arquivos fora das extensões permitidas
            if ext not in allowed_exts:
                try:
                    os.remove(file_path)
                    if self.log_hook:
                        self.log_hook(f"[CLEANUP] Arquivo removido (ext não permitida): {file_path}")
                except OSError as e:
                    if self.log_hook:
                        self.log_hook(f"[ERROR] Falha ao remover arquivo: {file_path} — {e}")


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

    def _is_cached_final(self, info_dict):
        if self.keep_original_file:
            return False

        return self._find_existing_file_by_id(info_dict)

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
        playlist_selection = None

        if self.allow_playlist and self.selected_entries:
            playlist_selection = [
                {
                    "id": e.get("id"),
                    "title": e.get("title"),
                    "playlist_title": e.get("playlist_title")
                }
                for e in self.selected_entries
                if e.get("id")
            ]

        state = {
            "url": self.url,
            "output_path": self.output_path,
            "audio_format": self.audio_format,
            "quality": self.quality,
            "allow_playlist": self.allow_playlist,
            "keep_original": self.keep_original_file,
            "normalize_enabled": self.normalize_enabled,
            "paused": paused,
            "playlist_selection": playlist_selection
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
        files = []

        if not self.tmp_dir or not os.path.exists(self.tmp_dir):
            return files

        for root, _, filenames in os.walk(self.tmp_dir):
            for name in filenames:
                if not name.lower().endswith(f".{self.audio_format.lower()}"):
                    continue

                tmp_file = os.path.join(root, name)

                # calcula path final REAL
                rel = os.path.relpath(tmp_file, self.tmp_dir)
                final_file = os.path.join(self.output_path, rel)

                files.append((tmp_file, final_file))

        return files

    def _find_existing_file_by_id(self, info_dict):
        """
        Procura no diretório final um arquivo que contenha o ID do vídeo.
        Independe de playlist, normalize ou sanitize.
        """

        video_id = info_dict.get("id")
        if not video_id:
            return None

        ext = f".{self.audio_format.lower()}"

        search_root = self.output_path

        if self.allow_playlist and self.playlist_dir:
            search_root = self.playlist_dir

        for root, _, files in os.walk(search_root):
            for f in files:
                if video_id in f and f.lower().endswith(ext):
                    return os.path.join(root, f)

        return None


    def get_playlist_folder_name(self, info):
        _ = self
        title = info.get("title", "Playlist")
        return sanitize_filename(title)

    def _should_download(self, base_path: str) -> bool:
        """
        Decide se deve baixar o arquivo novamente.

        base_path = caminho FINAL sem extensão
        Ex:
          C:/Downloads/Musica [abc123]
          C:/Downloads/Playlist/Musica [abc123]
        """

        audio_path = base_path + f".{self.audio_format.lower()}"
        video_path = base_path + ".mp4"

        audio_exists = os.path.exists(audio_path)
        video_exists = os.path.exists(video_path)

        print("\n================ SHOULD DOWNLOAD ================")
        print(f"BASE PATH           : {base_path}")
        print(f"AUDIO PATH          : {audio_path}")
        print(f"VIDEO PATH          : {video_path}")
        print(f"AUDIO EXISTS        : {audio_exists}")
        print(f"VIDEO EXISTS        : {video_exists}")
        print(f"NORMALIZE ENABLED   : {self.normalize_enabled}")
        print(f"KEEP ORIGINAL VIDEO : {self.keep_original_file}")

        # =====================================================
        # 🔹 NORMALIZE ATIVADO
        # =====================================================
        if self.normalize_enabled:
            print("MODE: NORMALIZE ON")

            # 🔥 áudio não existe
            if not audio_exists:
                print("→ AUDIO DOES NOT EXIST → DOWNLOAD")
                return True

            # 🔥 áudio existe → verificar LUFS real
            try:
                normalized = is_normalized(audio_path)
                print(f"LUFS CHECK RESULT   : {normalized}")
            except Exception as e:
                print(f"[ERROR] LUFS CHECK FAILED → {e}")
                print("→ FORCE DOWNLOAD")
                return True

            if not normalized:
                print("→ AUDIO EXISTS BUT NOT NORMALIZED → DOWNLOAD")
                return True

            # 🔥 manter vídeo exige mp4
            if self.keep_original_file and not video_exists:
                print("→ AUDIO NORMALIZED BUT VIDEO MISSING → DOWNLOAD")
                return True

            print("→ AUDIO EXISTS AND IS NORMALIZED → SKIP DOWNLOAD")
            return False

        # =====================================================
        # 🔹 SEM NORMALIZE
        # =====================================================
        print("MODE: NORMALIZE OFF")

        if not self.keep_original_file:
            result = not audio_exists
            print(f"NO NORMALIZE | NO KEEP → RETURN {result}")
            return result

        result = not (audio_exists and video_exists)
        print(f"NO NORMALIZE | KEEP ORIGINAL → RETURN {result}")
        return result

    def _cleanup_empty_dirs(self, root):
        """
        Remove apenas diretórios vazios.
        Seguro para playlists.
        """
        if not root or not os.path.exists(root):
            return

        for current, dirs, files in os.walk(root, topdown=False):
            if not dirs and not files:
                try:
                    os.rmdir(current)
                    if self.log_hook:
                        self.log_hook(f"[CLEANUP] Pasta vazia removida: {current}")
                except OSError:
                    pass

    def _resolve_final_path(self, path, info):
        """
        Converte qualquer path (tmp ou final) para o path FINAL real.
        """

        path = os.path.abspath(path)

        # Se não usa normalize → já é final
        if not self.normalize_enabled:
            return path

        # Se está no temp_normalize → converte para destino final
        if self.tmp_dir and path.startswith(self.tmp_dir):
            rel = os.path.relpath(path, self.tmp_dir)

            return os.path.abspath(os.path.join(self.output_path, rel))

        return path