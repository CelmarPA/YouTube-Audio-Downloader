# ui/app_window.py

"""
Main Application Window
-----------------------

Provides the main user interface for the downloader application.
Includes theme support, language preparation, clipboard
integration, and logging controls.
"""

import os
import tkinter as tk
import webbrowser

from threading import Thread
from tkinter import ttk, messagebox
from typing import Callable, Dict, Optional

from controller.download_controller import DownloadController
from ui.playlist_frame import PlaylistFrame
from ui.tooltip import Tooltip
from widgets.folders import open_download_folder, download_dir, choose_folder


DOWNLOAD_DIR: str = os.path.abspath(download_dir)


class AppWindow(tk.Tk):
    """
    Main application window.
    """

    def __init__(self) -> None:
        super().__init__()

        self.controller: DownloadController = DownloadController(self)
        self.playlist_frame: PlaylistFrame = PlaylistFrame

        self.on_download_requested: Optional[Callable[[str], None]] = None
        self.on_playlist_requested: Optional[Callable[[str], None]] = None

        self.audio_format_var: tk.StringVar = tk.StringVar(value="mp3")
        self.audio_quality_var: tk.StringVar = tk.StringVar(value="192")
        self.output_path_var: tk.StringVar = tk.StringVar(value=DOWNLOAD_DIR)
        self.output_path: str = self.output_path_var.get()
        self.playlist_var: tk.BooleanVar = tk.BooleanVar(value=False)
        self.keep_original_var: tk.BooleanVar = tk.BooleanVar(value=False)
        self.normalize_var: tk.BooleanVar = tk.BooleanVar(value=False)

        self.title('YouTube Audio Downloader')
        self.geometry("700x500")
        self.minsize(650, 450)

        try:
            self.iconbitmap("assets/icon.ico")
        except Exception as e:
            _e: str = str(e)
            pass

        self.theme: str = "light"
        self.language: str = "en-US"

        self.pause_resume_button: ttk.Button = None
        self.cancel_button: ttk.Button = None

        self.translations: Dict[str, Dict[str, str]] = {
            "en-US": {
                "url": "Video or Playlist URL",
                "paste": "Paste URL from clipboard",
                "download": "Download",
                "download_btn": "Start downloading the file",
                "pause": "Pause",
                "resume": "Resume",
                "pause_resume_btn": "Pause and resume the download process",
                "cancel": "Cancel",
                "cancel_btn": "Cancel the current download",
                "playlist": "Playlist",
                "playlist_ckb": "Enable playlist download",
                "keep_original": "Keep Original",
                "keep_original_ckb": "Keep original video file after extraction",
                "normalize_audio": "Normalize audio",
                "normalize_ckb":  "Normalize audio to target LUFS (-14 dB)",
                "show_log": "Show log",
                "choose": "Choose folder to save downloads",
                "open": "Open the download folder",
                "audio_format": "Select audio output format",
                "audio_quality": "Select audio bitrate (kbps applies to MP3/M4A only)",
                "help": "Open help page",
                "theme": "Toggle light/dark theme",
            }
        }

        self.status_var: tk.StringVar = tk.StringVar(value="Ready")

        self.progress_var: tk.DoubleVar = tk.DoubleVar(value=0)
        self.saved_selection: dict = None

        self._configure_style()
        self._build_ui()
        self._apply_theme()

        self.is_paused: bool = False

        # =============================
        # Global download status
        # =============================
        self.STATE_DIR: str = os.path.join(os.path.dirname(__file__), "..", "download_state")
        os.makedirs(self.STATE_DIR, exist_ok=True)
        self.STATE_FILE: str = os.path.join(self.STATE_DIR, "download_state.json")

        # ===== When starting the application =====
        if os.path.exists(self.STATE_FILE):
            # If there is a paused download
            resume: bool = messagebox.askyesno(
                "Paused download found",
                "There is a paused download.\nDo you want to resume?"
            )

            if resume:
                # Marks that the app is resuming from a crash
                self._resume_from_state(self.STATE_FILE)

            else:
                # User chose not to resume → cleanup
                self._on_no_resume()

        self.protocol("WM_DELETE_WINDOW", self.on_window_close)

    # =========================
    # TRANSLATION
    # =========================
    def t(self, key: str) -> str:
        """Translate a UI string key."""

        return self.translations[self.language].get(key, key)

    # =========================
    # UI BUILDING
    # =========================
    def _build_ui(self) -> None:
        """Build all UI components."""

        self._build_header()
        self._build_url_section()
        self._build_options()
        self._build_actions()
        self._build_status_bar()
        self._build_save_folder()
        self._build_log()

    def _build_header(self) -> None:
        """
        Build the application header.

        This section displays the application title and provides
        quick-access controls, such as the light/dark theme toggle button.
        """

        header: ttk.Frame = ttk.Frame(self)
        header.pack(fill="x", padx=10, pady=5)

        ttk.Label(header, text="YouTube Audio Downloader", font=("TkDefaultFont", 14, "bold")).pack(side="left")

        # Help button
        self.help_btn: ttk.Button = ttk.Button(  # TODO: CHANGE TO A LOCAL HELP
            header,
            text="❔",
            width=3,
            command=self._open_help
        )
        self.help_btn.pack(side="right", padx=(5, 0))

        Tooltip(self.help_btn, self.t("help"))

        # Theme toggle button
        self.theme_btn: ttk.Button = ttk.Button(
            header,
            text="🌙",
            width=3,
            command=self.toggle_theme
        )
        self.theme_btn.pack(side="right")

        Tooltip(self.theme_btn, self.t("theme"))

    def _build_url_section(self) -> None:
        """
        Build the URL input section.

        This section allows the user to paste or type a YouTube URL,
        providing both keyboard shortcuts (Ctrl+V) and a paste button
        for improved usability.
        """

        frame: ttk.Frame = ttk.Frame(self)
        frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame, text=self.t("url")).pack(anchor="w")

        row: ttk.Frame = ttk.Frame(frame)
        row.pack(fill="x")

        self.url_entry: ttk.Entry = ttk.Entry(row)
        self.url_entry.pack(side="left", fill="x", expand=True)

        paste_btn: ttk.Button = ttk.Button(
            row,
            text="📋",
            width=3,
            command=self._paste_url
        )
        paste_btn.pack(side="left", pady=(5, 0))

        Tooltip(paste_btn, self.t("paste"))

    def _build_options(self) -> None:
        """
        Build additional options section including audio format, quality,
        and user-selectable options: Playlist, Keep Original, Normalize Audio.
        """

        frame: ttk.Frame = ttk.Frame(self, height=30)
        frame.pack(fill="x", padx=10, pady=10)
        frame.pack_propagate(False)

        # -------------------------
        # Audio Format
        # -------------------------
        ttk.Label(frame, text="Audio Format:").pack(side="left")

        format_options: list = ["mp3", "wav", "flac", "m4a"]

        self.audio_format_menu: ttk.Combobox = ttk.Combobox(
            frame,
            textvariable=self.audio_format_var,
            values=format_options,
            width=5,
            state="readonly"
        )
        self.audio_format_menu.pack(side="left", padx=(5, 15))

        Tooltip(self.audio_format_menu, self.t("audio_format"))

        # -------------------------
        # Audio Quality
        # -------------------------
        ttk.Label(frame, text="Audio Quality (kbps):").pack(side="left", padx=(0, 5))

        quality_options: list = ["128", "192", "256", "320"]

        self.audio_quality_menu: ttk.Combobox = ttk.Combobox(
            frame,
            textvariable=self.audio_quality_var,
            values=quality_options,
            width=7,
            state="readonly"
        )
        self.audio_quality_menu.pack(side="left", padx=(5, 15))

        Tooltip(self.audio_quality_menu, self.t("audio_quality"))

        # -------------------------
        # Checkbuttons for extra options
        # -------------------------
        self.playlist_ckb: tk.Checkbutton = tk.Checkbutton(
            frame,
            text=self.t("playlist"),
            variable=self.playlist_var
        )
        self.playlist_ckb.pack(side="left", padx=(0, 10))

        Tooltip(self.playlist_ckb, self.t("playlist_ckb"))

        self.keep_original_ckb: tk.Checkbutton = tk.Checkbutton(
            frame,
            text=self.t("keep_original"),
            variable=self.keep_original_var
        )
        self.keep_original_ckb.pack(side="left", padx=(0, 10))

        Tooltip(self.keep_original_ckb, self.t("keep_original_ckb"))

        self.normalize_ckb: tk.Checkbutton = tk.Checkbutton(
            frame,
            text=self.t("normalize_audio"),
            variable=self.normalize_var
        )
        self.normalize_ckb.pack(side="left", padx=(0, 10))

        Tooltip(self.normalize_ckb, self.t("normalize_ckb"))

    def _build_actions(self) -> None:
        """
        Build the main action buttons section.

        This section contains the primary actions of the application,
        such as starting a download or opening the playlist selection.
        """

        frame: ttk.Frame = ttk.Frame(self)
        frame.pack(fill="x", padx=10, pady=5)

        self.download_btn: ttk.Button = ttk.Button(
            frame,
            text=self.t("download"),
            command=self.start_download
        )
        self.download_btn.pack(side="left", padx=(5, 0))

        Tooltip(self.download_btn, self.t("download_btn"))

        self.pause_resume_btn: ttk.Button = ttk.Button(
            frame,
            text=self.t("pause"),
            command=self.on_pause_resume_clicked,
            state="disabled"
        )
        self.pause_resume_btn.pack(side="left", padx=(5, 0))

        Tooltip(self.pause_resume_btn, self.t("pause_resume_btn"))

        self.cancel_btn: ttk.Button = ttk.Button(
            frame,
            text=self.t("cancel"),
            command=self.on_cancel_clicked,
            state="disabled"
        )
        self.cancel_btn.pack(side="left", padx=(5, 0))

        Tooltip(self.cancel_btn, self.t("cancel_btn"))

        self.open_btn: ttk.Button = ttk.Button(
            frame,
            text="Open Folder",
            command=self._open_folder)
        self.open_btn.pack(side="left", padx=(5, 0))

        Tooltip(self.open_btn, self.t("open"))

    def _build_save_folder(self) -> None:
        """
        Build the folder selection UI section.

        Allows the user to choose the download destination folder.
        """

        frame: ttk.Frame = ttk.Frame(self)
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame, text="Save in:").pack(side="left")

        self.output_entry: ttk.Entry = ttk.Entry(frame, textvariable=self.output_path_var)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(5, 5))

        choose_btn: ttk.Button = ttk.Button(frame, text="Choose...", command=self._choose_folder)
        choose_btn.pack(side="left")

        Tooltip(choose_btn, self.t("choose"))

    def _build_log(self) -> None:
        """
        Build the log panel with visibility toggle.

        This section contains a checkbox that allows the user to
        show or hide the log output, as well as a text widget used
        to display informational and error messages.
        """

        container: ttk.Frame = ttk.Frame(self)
        self.log_container = container

        container.pack(fill="both", expand=True, padx=10, pady=5)

        self.show_log_var = tk.BooleanVar(value=True)

        chk: tk.Checkbutton = tk.Checkbutton(
            container,
            text=self.t("show_log"),
            variable=self.show_log_var,
            command=self._toggle_log
        )
        chk.pack(anchor="w")


        self.log_text: tk.Text = tk.Text(
            container,
            height=10,
            state="disabled"
        )
        self.log_text.pack(fill="both", expand=True, pady=(5, 0))

    def _build_status_bar(self) -> None:
        """
        Build the application status bar.

        Displays short messages that reflect the current
        state of the application (idle, working, errors, etc.).
        """

        frame: ttk.Frame = ttk.Frame(self)
        frame.pack(fill="x", padx=10, pady=(0, 5))

        ttk.Label(
            frame,
            textvariable=self.status_var,
            anchor="w",
            foreground="gray"
        ).pack(fill="x")

        # Progress bar
        self.progress_bar: ttk.Progressbar = ttk.Progressbar(
            frame,
            variable=self.progress_var,
            maximum=100,
            mode="determinate",
        )
        self.progress_bar.pack(fill="x", padx=(4, 0))

    def _paste_url(self, _: Optional[tk.Event] = None) -> None:
        """
        Paste text from the system clipboard into the URL entry.

        Safely handles empty or unavailable clipboard content.
        """

        try:
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, self.clipboard_get())

        except tk.TclError:
            pass

    def _toggle_log(self) -> None:
        """
        Toggle visibility of the log output area.

        Allows users to keep the interface clean when logs
        are not needed.
        """

        if self.show_log_var.get():
            self.log_text.pack(fill="both", expand=True, pady=(5, 0))

        else:
            self.log_text.pack_forget()

    def toggle_theme(self) -> None:
        """
        Toggle between light and dark application themes.
        """

        self.theme = "dark" if self.theme == "light" else "light"
        self._apply_theme()

    def _configure_style(self) -> None:
        """
        Configure the base ttk styling.

        Uses the default ttk theme as a foundation for
        custom light and dark themes.
        """

        self.style: ttk.Style = ttk.Style(self)
        self.style.theme_use("default")

    def _apply_theme(self) -> None:
        """
        Apply the current theme colors to the main window.

        Adjusts background and foreground colors dynamically based on the
        selected theme. Updates main window, child widgets, and ttk styles.
        """

        if self.theme == "dark":
            bg = "#1e1e1e"
            fg = "#ffffff"
            entry_bg = "#2e2e2e"
            entry_fg = "#ffffff"
            btn_bg = "#3a3a3a"
            btn_fg = "#ffffff"
            btn_hover_bg = "#505050"
            ckb_bg = "#1e1e1e"
            ckb_fg = "#ffffff"
            ckb_hover_bg = "#333333"
        else:
            bg = "#f5f5f5"
            fg = "#000000"
            entry_bg = "#ffffff"
            entry_fg = "#000000"
            btn_bg = "#e0e0e0"
            btn_fg = "#000000"
            btn_hover_bg = "#c0c0c0"
            ckb_bg = "#f5f5f5"
            ckb_fg = "#000000"
            ckb_hover_bg = "#e8e8e8"

        # Main window background
        self.configure(bg=bg)

        # Configure ttk styles
        style = self.style
        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("TButton", background=btn_bg, foreground=btn_fg)
        style.map(
            "TButton",
            background=[("active", btn_hover_bg)],
            foreground=[("active", btn_fg)]
        )
        style.configure("TCheckbutton", background=ckb_bg, foreground=ckb_fg)
        style.map(
            "TCheckbutton",
            background=[("active", ckb_hover_bg)],
            foreground=[("active", ckb_fg)]
        )

        # Recursively apply colors to child widgets (for non-ttk widgets)
        def _recursive_apply(widget):
            for child in widget.winfo_children():
                cls = child.winfo_class()
                try:
                    if cls in ("TFrame", "Frame"):
                        child.configure(background=bg)
                    elif cls in ("TLabel", "Label"):
                        child.configure(background=bg, foreground=fg)
                    elif cls in ("TButton", "Button"):
                        child.configure(background=btn_bg, foreground=btn_fg)
                    elif cls in ("TEntry", "Entry"):
                        child.configure(background=entry_bg, foreground=entry_fg)
                    elif cls in ("Text",):
                        child.configure(background=entry_bg, foreground=entry_fg)
                    elif cls in ("TCheckbutton", "Checkbutton"):
                        child.configure(background=ckb_bg, foreground=ckb_fg)
                except tk.TclError:
                    pass
                _recursive_apply(child)

        _recursive_apply(self)

    # =========================
    # Download
    # =========================
    def start_download(self) -> None:
        url: str = self.url_entry.get().strip()

        if not self._validate_url(url):
            return

        self.set_downloading_state()

        self.progress_var.set(0)
        self.status_var.set("Initiating...")

        Thread(target=self.run_download, daemon=True).start()

    def run_download(self) -> None:
        os.makedirs(self.output_path_var.get(), exist_ok=True)

        options: dict = {
            "output_path": self.output_path.strip(),
            "audio_format": self.audio_format_var.get(),
            "audio_quality": self.audio_quality_var.get(),
            "allow_playlist": self.playlist_var.get(),
            "keep_original": self.keep_original_var.get(),
            "normalize_enabled": self.normalize_var.get(),
            "progress_hook": self.on_progress,
            "status_hook": self.set_status,
            "file_finished_hook": self.on_file_finished,
            "error_hook": self.on_error,
            "log_hook": self._log,
            "state_file": self.STATE_FILE
        }

        url: str = self.url_entry.get().strip()

        self.controller.download(url, options)

    # =========================
    # LOGGING
    # =========================
    def _log(self, message: str, level: str = "INFO") -> None:
        """
        Write a message to the log output area.

        The log entry is timestamped and displayed in the
        application's log panel. This method is designed
        to be easily extended in the future to support
        file logging or external logging systems.

        Args:
            message (str): The message to be logged.
            level (str): Log level (e.g., INFO, WARNING, ERROR).
        """

        from datetime import datetime

        timestamp: str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        entry: str = f"[{timestamp}] {level}: {message}\n"

        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, entry)
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")

    # =========================
    # VALIDATION
    # =========================
    def _validate_url(self, url: str) -> bool:
        """
        Validate whether the provided URL appears to be a valid YouTube URL.

        This method performs a lightweight validation to prevent
        empty inputs or obviously invalid URLs from triggering
        download actions.

        Args:
            url (str): URL entered by the user.

        Returns:
            bool: True if the URL is valid enough to proceed, False otherwise.
        """

        if not url:
            self._log("No URL provided", level="ERROR")
            self._show_error("Please enter a YouTube URL.")

            return False

        if not self._looks_like_youtube_url(url):
            self._log(f"Invalid YouTube URL: {url}", level="ERROR")
            self._show_error("Invalid YouTube URL.")

            return False

        return True

    @staticmethod
    def _looks_like_youtube_url(url: str) -> bool:
        """
        Check if the URL matches common YouTube URL patterns.

        Args:
            url (str): URL to check.

        Returns:
            bool: True if URL resembles a YouTube URL.
        """

        import re

        pattern = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"

        return bool(re.match(pattern, url))

    @staticmethod
    def _show_error(message: str) -> None:
        """
        Display an error message dialog to the user.

        Args:
            message (str): Error message to display.
        """

        from tkinter import messagebox

        messagebox.showerror("Error", message)

    def _set_status(self, message: str) -> None:
        """
       Update the application status message.

       :param message: Status text to display.
       :type message: str
       """

        self.status_var.set(message)

    def _choose_folder(self) -> None:
        """Open a folder selection dialog and update the output path."""

        folder: Optional[str] = choose_folder()

        if folder:
            self.output_path_var.set(folder)

    def _open_folder(self) -> None:
        """Open the current output folder in the system file explorer."""

        open_download_folder(self.output_path_var.get())

    @staticmethod
    def _open_help() -> None:
        """Open the help webpage or local help file."""
        webbrowser.open("https://github.com/your-repo/help")

    def on_pause_resume_clicked(self) -> None:
        if not self.is_paused:
            # Pause
            self.controller.pause()
            self.is_paused = True
            self.pause_resume_btn.config(text=self.t("resume"))

        else:
            # Resume
            self.controller.resume()
            self.is_paused = False
            self.pause_resume_btn.config(text=self.t("pause"))

    def on_cancel_clicked(self) -> None:
        if not hasattr(self, "controller") or not self.controller:
            return

        # Playlist
        if self.playlist_var.get():
            confirm = messagebox.askyesno(
                "Cancel playlist",
                "Do you wish to cancel after the current item finishes?"
            )

            if not confirm:
                return

            self.controller.cancel(after_current=True)

            self.status_var.set("⏭️ Finishing current playlist item...")
            self._log(
                "⏭️ Cancellation requested: waiting for current item to finish.",
                level="CANCEL"
            )


        # Single
        else:
            self.controller.cancel(after_current=False)

            self.status_var.set("Canceling download...")
            self._log("❌ Cancellation requested: download will be interrupted immediately.", level="CANCEL")

        self.cancel_btn.config(state="disabled")

    def _resume_from_state(self, path: str) -> None:
        import json

        with open(path, "r", encoding="utf-8") as f:
            state = json.load(f)

        self.url_entry.insert(0, state["url"])
        self.audio_format_var.set(state["audio_format"])
        self.audio_quality_var.set(state["quality"])
        self.playlist_var.set(state["allow_playlist"])
        self.keep_original_var.set(state["keep_original"])
        self.normalize_var.set(state["normalize_enabled"])
        self.output_path_var.set(state.get("output_path", download_dir))
        self.saved_selection = state.get("playlist_selection")

        self.start_download()

    def on_window_close(self):

        if hasattr(self, "downloader") and self.downloader:
            try:
                # Saves status only if download is active or paused
                self.controller.on_window_close()

            except Exception as e:
                _e = e
                pass

        self.destroy()

    def _on_no_resume(self):
        """Action taken when the user decides not to resume the paused download."""

        try:
            os.remove(self.STATE_FILE)

        except FileNotFoundError:
            pass

        # Optional: log
        self._log("Download paused, discarded by user.")

    # =========================
    # Hooks (THREAD-SAFE)
    # =========================
    def on_progress(
        self,
        percent: float,
        item_index: Optional[int] = None,
        total_items: Optional[int] = None,
        status_text: Optional[str] = None
    ) ->None:
        """
        Update progress bar and status.

        :param percent: 0 to 100
        :type percent: float
        :param item_index: current playlist index (optional)
        :type item_index: int
        :param total_items: total number of items in the playlist (optional)
        :type total_items: int
        :param status_text: optional detailed text
        :type status_text: str
        """

        percent: float = min(max(percent, 0), 100)

        def update():
            self.progress_var.set(percent)

            # create a status if detailed text wasn't provided
            if not status_text:
                text: str = f"Progresso: {percent:.1f}%"
                if item_index and total_items:
                    text: str = f"Item {item_index}/{total_items} — {text}"
            else:
                text: str = status_text

            self.status_var.set(text)

        self.after(0, update)

    def set_status(self, text) -> None:
        """
        Set current status.

        :param text: Status text.
        :type text: str
        """

        self.after(0, lambda: self.status_var.set(text))

    def on_file_finished(self, filename) -> None:
        """
        Displays the final log and resets progress_var.

        :param filename: Name of the file to display.
        :type filename: str
        """

        def update():
            self._log(f"Completed: {os.path.basename(filename)}")
            self.progress_var.set(0)

        self.after(0, update)

    def on_error(self, message) -> None:
        """
        Log the error that occurred.

        :param message: Error message.
        :type message: str
        """
        self.after(0, lambda: messagebox.showerror("Error", message))

    def show_mix_warning(self) -> None:
        """
        Displays a warning message explaining that YouTube MIX playlists
        cannot be downloaded as regular playlists.
        """

        messagebox.showwarning(
            title="YouTube MIX detected",
            message=(
                "YouTube MIX playlists are automatically generated and customizable.\n\n"
                "They may contain up to 5,000 videos and do not represent a fixed playlist.\n\n"
                "For this reason, playlist download is not supported for MIX content.\n\n"
                "The playlist option will be disabled."
            )
        )

        self.playlist_var.set(False)

    # =========================
    # UI STATES (CALLED BY CONTROLLER)
    # =========================
    def set_idle_state(self) -> None:
        """
        Set the UI to the idle state.

        Enables the download button, disables pause/resume and cancel buttons,
        resets the paused flag, and updates the status to indicate the application
        is ready.
        """

        self.download_btn.config(state="normal")
        self.pause_resume_btn.config(text=self.t("pause"), state="disabled")
        self.cancel_btn.config(state="disabled")
        self.is_paused = False
        self.status_var.set("Ready")

    def set_downloading_state(self) -> None:
        """
        Set the UI to the downloading state.

        Disables the download button, enables pause/resume and cancel buttons,
        and ensures the paused flag is reset.
        """

        self.download_btn.config(state="disabled")
        self.pause_resume_btn.config(text=self.t("pause"), state="normal")
        self.cancel_btn.config(state="normal")
        self.is_paused = False

    def set_playlist_selection_state(self) -> None:
        """
        Set the UI state while selecting a playlist.

        Disables pause/resume and cancel buttons to prevent user interaction
        during playlist selection.
        """

        self.pause_resume_btn.config(state="disabled")
        self.cancel_btn.config(state="disabled")

    @staticmethod
    def notify_auth_failed() -> None:
        """Alerts when video is restricted."""

        messagebox.showwarning(
            "Restricted video skipped",
            "A private or age-restricted video could not be downloaded and was skipped."
        )
