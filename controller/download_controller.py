# controller/download_controller.py

import os
import threading
import yt_dlp

from typing import Callable, Optional, TYPE_CHECKING, List

from core.downloader import Downloader
from ui.playlist_frame import PlaylistFrame
from utils.helpers import mark_already_downloaded
from ui.dialogs.themed_messagebox import ThemedMessageBox

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
    ) -> None:
        """
        Initialize the download controller.

        :param app_window: Main application window instance.
        :type app_window: AppWindow
        :param progress_hook: Callback for progress updates.
        :type progress_hook: Callable or None
        :param status_hook: Callback for status messages.
        :type status_hook: Callable or None
        :param file_finished_hook: Callback triggered when a file finishes downloading.
        :type file_finished_hook: Callable or None
        :param error_hook: Callback for error notifications.
        :type error_hook: Callable or None
        :param log_hook: Callback for log messages.
        :type log_hook: Callable or None
        """

        self.app_window = app_window

        # Current downloader instance
        self.downloader: Optional[Downloader] = None
        self.thread: Optional[threading.Thread] = None

        # Download state
        self.active: bool = False
        self.paused: bool = False
        self._alerted_private: bool = False

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

        self._alerted_private = False

        if self.active:
            return  # Safety check to avoid double start

        self.active: bool = True
        self.paused: bool = False

        self.thread = threading.Thread(
            target=self._run_download,
            args=(url, options),
            daemon=True
        )
        self.thread.start()

    def pause(self) -> None:
        """
        Pause the active download.
        If the downloader is not yet initialized, the pause is deferred.
        """

        # Downloader nor ready yet → defer pause
        if not self.downloader:
            self.pending_pause: bool = True

            return

        if self.paused:
            return

        self.downloader.pause()
        self.paused = True

    def resume(self) -> None:
        """
        Resume a previously paused download.
        """

        if not self.downloader or not self.paused:
            return

        self.downloader.resume()
        self.paused = False

    def cancel(self, after_current: bool = False) -> None:
        """
        Cancel the active download.

        :param after_current: If True, cancel after the current playlist item finishes.
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
        Initializes the Downloader and manages the full download lifecycle.

        :param url: YouTube video or playlist URL.
        :type url: str
        :param options: Download configuration options.
        :type options: dict
        """

        options: Optional[dict] = options or {}

        try:
            # ================================
            # SAFE CHECK — no playlist expansion
            # ================================
            basic_info = self.extract_basic_info(url)

            if not isinstance(basic_info, dict):
                basic_info = {}

            title = (basic_info.get("title") or "").lower()

            if title in ("[private video]", "[restricted video]"):
                basic_info["__restricted__"] = "private"

            elif "age" in (basic_info.get("availability") or ""):
                basic_info["__restricted__"] = "age"

            if basic_info.get("__restricted__") and not options.get("use_cookies"):
                self._log(self.app_window.i18n.t("download_controller.log_restricted"), level=self.app_window.i18n.t("auth"))

                self._emit_error(
                    self.app_window.i18n.t("download_controller.error_restricted_msg"),
                    title=self.app_window.i18n.t("download_controller.error_restricted_title"),
                    level=self.app_window.i18n.t("auth")
                )
                return

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
                resolution=options.get("video_resolution", "Auto"),
                allow_playlist=options.get("allow_playlist", False),
                keep_original_file=options.get("keep_original", False),
                normalize_enabled=options.get("normalize_enabled", False),
                progress_hook=options.get("progress_hook", None),
                status_hook=options.get("status_hook", None),
                file_finished_hook=options.get("file_finished_hook", None),
                error_hook=options.get("error_hook", None),
                log_hook=options.get("log_hook", None),
                confirm_keep_hook=self.confirm_keep_current_file,
                state_file=options.get("state_file", None),
                language=options.get("language", "en-US"),
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

                self._set_status(self.app_window.i18n.t("download_controller.status_loading_playlist"))

                # Extract full playlist info (flat + fast)
                info: dict = self.extract_playlist_flat(url)

                if not isinstance(info, dict) or not info.get("entries"):
                    self._emit_error(
                        self.app_window.i18n.t("download_controller.error_not_info"),
                        title=self.app_window.i18n.t("download_controller.error_not_info_title"),
                        level=self.app_window.i18n.t("auth")
                    )
                    return
                entries: List[dict] = []

                for e in info.get("entries", []):
                    if not e or not e.get("id"):
                        continue

                    restricted = None

                    title = (e.get("title") or "").lower()
                    duration = e.get("duration")

                    # 🔒 Private video (flat stub)
                    if title == "[private video]":
                        restricted = "private"

                    # 🔞 Age restricted (yt-dlp usually keeps title normal)
                    elif e.get("availability") == "age_restricted":
                        restricted = "age"

                    # 🔞 fallback: duration missing + not playable
                    elif duration is None and not e.get("is_playable", True):
                        restricted = "age"

                    if restricted:
                        e["__restricted__"] = restricted

                    entries.append(e)

                    self._set_status(f"📋 {len(entries)} {self.app_window.i18n.t('download_controller.status_entries')}")

                if not entries:
                    self._log(self.app_window.i18n.t("download_controller.log_not_entries"), level=self.app_window.i18n.t("error_level"))

                    return

                playlist_title: str = info.get("title", "Playlist")
                self.downloader.playlist_title = playlist_title

                # Restore saved selection
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

                if not selected_entries:
                    self._log(self.app_window.i18n.t("download_controller.log_not_selected_entries"), level=self.app_window.i18n.t("cancel_level"))

                    return

                # 🔥 downloader will download only these
                self.downloader.selected_entries = selected_entries
                self.downloader.is_manual_selection = True
                self.downloader.url = None  # 🔥

            # ================================
            # DEFERRED CANCEL — abort before start
            # ================================
            if self.pending_cancel:
                self._log(self.app_window.i18n.t("download_controller.log_pending_cancel"), level=self.app_window.i18n.t("cancel_level"))

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
            if self.downloader and self.downloader.STATE_FILE:
                self.downloader.save_state(paused=True)

            # Starts the download
            try:
                self.downloader.start()

            except RuntimeError as e:
                msg = str(e)

                if msg.startswith("AUTH_REQUIRED::"):
                    self._handle_auth_required(msg)

                else:
                    self._error(msg)

        finally:
            # Reset controller state
            self.pending_pause: bool = False
            self.pending_cancel: bool = False
            self.pending_cancel_after_current: bool = False


            self.active: bool = False
            self.paused: bool = False
            self.downloader = None

            self.app_window.after(0, self.app_window.set_idle_state)

    def on_window_close(self) -> None:
        """
        Persist download state when the application window is closed.
        """

        if self.downloader:
            self.downloader.save_state_on_close()

    # ===============================
    # Internal logging
    # ===============================
    def _log(self, message: str, level: str = "INFO") -> None:
        """
        Internal logger for controller messages.

        :param message: Log message.
        :type message: str
        :param level: Log level.
        :type level: str
        """

        from datetime import datetime

        if level == "INFO":
            level: str = self.app_window.i18n.t("info")

        timestamp: str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        entry: str = f"[{timestamp}] {level}: {message}\n"

        if self.log_hook:
            self.log_hook(entry)

    def  _set_status(self, message: str) -> None:
        """
        Update the UI status message.

        :param message: The status message.
        :type message: str
        """

        if self.status_hook:
            self.status_hook(message)

    def _error(self, message: str) -> None:
        """
        Emit an error message through the error hook.

        :param message: Error message.
        :type message: str
        """

        if self.error_hook:
            self.error_hook(message)

    def _emit_error(
            self,
            message: str,
            title: str = "Download error",
            level: str = "ERROR",
            show_dialog: bool = True
    ) -> None:
        """
        Thread-safe error emitter.
        Shows UI dialog, logs error and notifies hooks.
        """

        if "[private video]" in message.lower() or "[restricted video]" in message.lower():
            if self._alerted_private:
                show_dialog = False
            else:
                self._alerted_private = True

        if title == "Download error":
            title = self.app_window.i18n.t("download_error")

        if level == "ERROR":
            level: str = self.app_window.i18n.t("error_level")

        self._log(message, level=level)
        self._error(message)

        if show_dialog:
            self.app_window.after(
                0,
                lambda: ThemedMessageBox.show_error(
                    parent=self.app_window,
                    title=title,
                    message=message,
                    theme=self.app_window.get_theme_context()
                )
            )

    @staticmethod
    def is_youtube_mix(info: dict) -> bool:
        """
        Determine whether the provided yt-dlp info represents a YouTube MIX.

        :param info: Extracted yt-dlp metadata.
        :type info: dict
        :return: True if the info represents a YouTube MIX.
        :rtype: bool
        """

        if not info:
            return False

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

    def _handle_auth_required(self, error_msg: str) -> None:
        """
        Handles videos that require authentication.

        :param error_msg: The error message.
        :type error_msg: str
        """

        _error_msg = error_msg

        if not self.downloader:
            return

        if self.downloader.auth_retry_attempted:
            self.downloader.skip_current_item("auth already attempted")

            return

        self.downloader.auth_retry_attempted = True

        self._set_status(self.app_window.i18n.t("download_controller.status_restricted"))

        self.downloader.retry_current_item()

    def extract_basic_info(self, url: str) -> dict:
        """
        Safely extract basic metadata without raising errors
        on private, age-restricted, or authentication-required videos.

        :param url: YouTube video or playlist URL.
        :type url: str
        :return: Extracted metadata dictionary.
        :rtype: dict
        """

        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "extract_flat": True,
            "ignoreerrors": True,
            "nocheckcertificate": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                # Resolve URL stub safely
                if isinstance(info, dict) and info.get("_type") == "url":
                    return info

                return info or {}

        except Exception as e:
            self._error(str(e))

            # 🔥 ABSOLUTE SAFETY
            return {
                "_type": "url",
                "title": "[Restricted video]",
                "__restricted__": "unknown",
            }

    @staticmethod
    def extract_playlist_flat(url: str) -> dict:
        """
        Perform a fast flat playlist extraction without authentication or download.

        :param url: YouTube video or playlist URL.
        :type url: str
        :return: Playlist metadata.
        :rtype: dict
        """

        ydl_opts: dict = {
            "quiet": True,
            "no_warming": True,
            "skip_download": True,
            "extract_flat": "in_playlist",
            "dump_single_json": True,
            "forcejson": True,
            "ignoreerrors": True,
            "playlist_items": None
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info: dict = ydl.extract_info(url, download=False)

            if info and info.get("_type") == "url":
                info: dict = ydl.extract_info(info["url"], download=False)

            return info or {}

    def confirm_keep_current_file(self, file_path: str) -> bool:
        """
        Thread-safe confirmation dialog asking whether to keep the current file.

        :param file_path: Path to the downloaded file.
        :type file_path: str
        :return: True if the user chooses to keep the file.
        :rtype: bool
        """

        filename = os.path.basename(file_path)

        # Directly show the modal dialog and get the result
        keep: bool = ThemedMessageBox.ask_yes_no(
            parent=self.app_window,
            title=self.app_window.i18n.t("download_controller.ask_user_title"),
            message=f"{self.app_window.i18n.t('download_controller.ask_user')}{filename}",
            theme=self.app_window.get_theme_context()
        )

        return keep
