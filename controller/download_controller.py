# controller/download_controller.py

import os
import threading
import yt_dlp
import yt_dlp.utils

from tkinter import messagebox
from typing import Callable, Optional, TYPE_CHECKING

from core.downloader import Downloader
from ui.playlist_frame import PlaylistFrame
from utils.helpers import mark_already_downloaded

if TYPE_CHECKING:
    from ui.app_window import AppWindow


class DownloadController:
    """
    Controller that manages download requests from the UI
    and communicates progress back to the UI.
    """

    def __init__(
        self,
        app_window: "AppWindow",
        progress_hook: Optional[Callable[[float, Optional[int], Optional[int], str], None]] = None,
        status_hook: Optional[Callable[[str], None]] = None,
        file_finished_hook: Optional[Callable[[str], None]] = None,
        error_hook: Optional[Callable[[str], None]] = None,
        log_hook: Optional[Callable[[str], None]] = None,
    ):
        self.app_window = app_window

        # Current downloader instance
        self.downloader: Optional[Downloader] = None
        self.thread: Optional[threading.Thread] = None

        # Download state
        self.active: bool = False
        self.paused: bool = False

        # Deferred pause support
        self.pending_pause: bool = False
        self.pending_cancel: bool = False
        self.pending_cancel_after_current: bool = False

        # Hooks for UI callbacks
        self.progress_hook = progress_hook
        self.status_hook = status_hook
        self.file_finished_hook = file_finished_hook
        self.error_hook = error_hook
        self.log_hook = log_hook

    # ===============================
    # Public methods for UI actions
    # ===============================
    def download(self, url: str, options: Optional[dict] = None) -> None:
        """
        Start a download in a separate thread to avoid blocking the UI.

        :param url: YouTube video or playlist URL.
        :type url: str
        :param options: Options for download.
        :type options: dict
        """

        if self.active:
            return  # safety: avoid double start

        self.active: bool = True
        self.paused: bool = False

        self.thread = threading.Thread(
            target=self._run_download,
            args=(url, options),
            daemon=True
        )
        self.thread.start()

    def pause(self) -> None:
        """Pause the active download or defer pause if downloader is not ready."""

        # Downloader nor ready yet → defer pause
        if not self.downloader:
            self.pending_pause: bool = True
            print("PAUSE DEFERRED (DOWNLOAD NOT READY YET")

            return

        if self.paused:
            return

        self.downloader.pause()
        self.paused = True

    def resume(self) -> None:
        """Resume a paused download."""

        if not self.downloader or not self.paused:
            return

        self.downloader.resume()
        self.paused = False

    def cancel(self, after_current: bool = False) -> None:
        """
        Cancel the active download.

        :param after_current: If True, cancel after current playlist item finishes.
        :type after_current: bool
        """

        if self.downloader is None:
            self.pending_cancel: bool = True
            self.pending_cancel_after_current: bool = after_current

            return

        self.downloader.cancel(after_current=after_current)

    def _run_download(self, url: str, options: Optional[dict] = None) -> None:
        """
        Internal method executed in a separate thread.
        Initializes the Downloader with provided format and quality.
        """

        options: Optional[dict] = options or {}

        try:
            # ================================
            # SAFE CHECK — no playlist expansion
            # ================================
            basic_info: dict = self.extract_basic_info(url)

            if options.get("allow_playlist") and self.is_youtube_mix(basic_info):
                self.app_window.after(0, self.app_window.show_mix_warning)

                # 🔥 force disable playlist
                options["allow_playlist"] = False

                return

            # ================================
            # INIT DOWNLOADER
            # ================================
            self.downloader = Downloader(
                url=url,
                output_path=options.get("output_path", ".downloads"),
                audio_format=options.get("audio_format", "mp3"),
                quality=options.get("audio_quality", "192"),
                allow_playlist=options.get("allow_playlist", False),
                keep_original_file=options.get("keep_original", False),
                normalize_enabled=options.get("normalize_enabled", False),
                progress_hook=options.get("progress_hook", None),
                status_hook=options.get("status_hook", None),
                file_finished_hook=options.get("file_finished_hook", None),
                error_hook=options.get("error_hook", None),
                log_hook=options.get("log_hook", None),
                state_file=options.get("state_file", None)
            )

            # ================================
            # DEFERRED CANCEL / PAUSE
            # ================================
            if self.pending_cancel:
                self.downloader.cancel(after_current=self.pending_cancel_after_current)

            self.downloader.pending_pause = self.pending_pause

            # 🔥 Apply deferred pause if user requested pause early
            if self.pending_pause:
                self.downloader.pause()
                self.paused: bool = True
                self.pending_pause: bool = False

            # ================================
            # PLAYLIST SELECTION FLOW
            # ================================
            if options.get("allow_playlist"):
                self.active = False
                self.paused = False
                self.app_window.after(0, self.app_window.set_playlist_selection_state)

                # Extract full playlist info (with auth retry)
                info = self.extract_info_with_auth_retry(url)

                if not info:
                    self.app_window.after(0, self.app_window.notify_auth_failed)

                    return

                # 🔥 Remove private/unavailable videos
                entries = [
                    e for e in info.get("entries", [])
                    if e and e.get("id")
                ]

                if not entries:
                    self._log("Playlist has no downloadable videos", level="ERROR")
                    return

                playlist_title: str = info.get("title", "Playlist")

                if self.app_window.saved_selection:
                    saved_ids = {
                        e["id"] for e in self.app_window.saved_selection if "id" in e
                    }
                    for entry in entries:
                        entry["__preselected__"] = entry["id"] in saved_ids

                playlist_dir = os.path.join(
                    self.app_window.output_path_var.get(),
                    self.downloader.get_playlist_folder_name(info)
                )

                mark_already_downloaded(
                    entries=entries,
                    playlist_dir=playlist_dir,
                    audio_format=self.app_window.audio_format_var.get(),
                    keep_original=self.app_window.keep_original_var.get(),
                    normalize_audio=self.app_window.normalize_var.get()
                )

                playlist_window: PlaylistFrame = self.app_window.playlist_frame(
                    master=self.app_window,
                    playlist_title=playlist_title,
                    entries=entries,
                    theme=self.app_window.theme
                )
                self.app_window.wait_window(playlist_window)

                self.app_window.after(0, self.app_window.set_playlist_selection_state)

                selected_entries = playlist_window.selected

                if selected_entries is None or len(selected_entries) == 0:
                    self._log("No videos selected, download canceled", level="CANCEL")

                    return

                # Only the selected items are available for download.
                self.downloader.selected_entries = selected_entries

            # ================================
            # DEFERRED CANCEL — abort before start
            # ================================
            if self.pending_cancel:
                self._log("Download aborted before start", level="CANCEL")

                self.pending_cancel = False
                self.pending_cancel_after_current = False

                return

            # ================================
            # DOWNLOAD IS REALLY STARTING NOW
            # ================================
            self.active = True
            self.paused = False

            self.app_window.after(0, self.app_window.set_downloading_state)

            # 🔥 Save state immediately (fix silent close bug)
            if self.downloader is not None and self.downloader.STATE_FILE:
                self.downloader.save_state()

            # Starts the download
            try:
                self.downloader.start()

            except RuntimeError as e:
                msg = str(e)

                if msg.startswith("AUTH_REQUIRED::"):
                    self._handle_auth_required(msg)

                else:
                    if self.error_hook:
                        self.error_hook(msg)

        finally:
            self.pending_pause: bool = False
            self.pending_cancel: bool = False
            self.pending_cancel_after_current: bool = False


            self.active: bool = False
            self.paused: bool = False
            self.downloader = None

            self.app_window.after(0, self.app_window.set_idle_state)

    def on_window_close(self) -> None:
        if self.downloader:
            self.downloader.save_state_on_close()

    # ===============================
    # Internal logging
    # ===============================
    def _log(self, message: str, level: str = "INFO") -> None:
        """Internal logger for controller messages."""

        from datetime import datetime

        timestamp: str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        entry: str = f"[{timestamp}] {level}: {message}\n"

        if self.log_hook:
            self.log_hook(entry)

    @staticmethod
    def is_youtube_mix(info: dict) -> bool:
        """
        Determines whether the provided yt-dlp info represents a YouTube MIX.
        """
        playlist_id: str = info.get("playlist_id", "") or ""
        webpage_url: str = info.get("webpage_url", "") or ""

        return (
                info.get("is_mix") is True
                or playlist_id.startswith("RD")
                or (
                        info.get("webpage_url_basename") == "watch"
                        and "list=RD" in webpage_url
                )
        )

    @staticmethod
    def extract_basic_info(url: str) -> dict:
        """
        Extracts minimal YouTube metadata without resolving playlist entries.

        This method is safe for MIX and large playlists, as it avoids
        full playlist expansion.

        :param url: YouTube video or playlist URL
        :return: Minimal yt-dlp info dictionary
        """
        ydl_opts: dict = {
            "quiet": True,
            "skip_download": True,
            "extract_flat": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info: dict = ydl.extract_info(url, download=False)

            # yt-dlp may return a URL stub first
            if info.get("_type") == "url":
                info = ydl.extract_info(info["url"], download=False)

        return info

    def _handle_auth_required(self, error_msg: str):
        """Handles videos that require authentication."""

        _error_msg = error_msg

        if not self.downloader:
            return

        if self.downloader.auth_retry_attempted:
            self.downloader.skip_current_item("auth already attempted")

            return

        self.downloader.auth_retry_attempted = True
        self.downloader.set_browser_cookies("default")

        if self.status_hook:
            self.status_hook("🔐 Restricted video, retrying with browser cookies...")

        self.downloader.retry_current_item()

    def _handle_auth_failed(self) -> None:
        """Alerts when video is restricted."""

        messagebox.showwarning(
            "Restricted video skipped",
            "A private or age-restricted video could not be downloaded and was skipped."
        )

        self.downloader.skip_current_item()

    def extract_info_with_auth_retry(self, url: str) -> Optional[dict]:
        """
        Extracts video/playlist info.
        If authentication is required, retries automatically using browser cookies.

        :param url: YouTube video or playlist URL
        :type url: str
        """

        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "ignoreerrors": True,
            "extract_flat": False,
        }

        # 1️⃣ First attempt (no cookies)
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)

        except (yt_dlp.utils.ExtractorError, yt_dlp.utils.DownloadError) as e:
            msg = str(e).lower()

            if not any(k in msg for k in ("private", "sign in", "age", "cookies")):
                raise   # not auth-related → real error

        # 2️⃣ Retry with browser cookies
        try:
            ydl_opts["cookiesfrombrowser"] = ("default",)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if self.log_hook:
                    self._log("Retrying extraction with browser cookies", level="AUTH")

                    return ydl.extract_info(url, download=False)

        except (yt_dlp.utils.ExtractorError, yt_dlp.utils.DownloadError) as e:
            return None  # Definitive failure