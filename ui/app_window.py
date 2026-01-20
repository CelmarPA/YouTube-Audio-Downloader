# ui/app_window.py

"""
Main Application Window
-----------------------

Provides the main user interface for the downloader application.
Includes theme support, language preparation, clipboard
integration, and logging controls.
"""

import os
import sys
import tkinter as tk
import subprocess

from threading import Thread
from tkinter import ttk
from typing import Callable, Optional

from controller.download_controller import DownloadController
from ui.playlist_frame import PlaylistFrame
from ui.tooltip import Tooltip
from widgets.folders import open_download_folder, download_dir, choose_folder
from i18n.manager import I18nManager
from ui.help_window import HelpWindow
from utils.paths import resource_path
from utils.window import set_window_icon
from utils.app_config import load_config, save_config
from ui.dialogs.themed_messagebox import ThemedMessageBox


DOWNLOAD_DIR: str = os.path.abspath(download_dir)


class AppWindow(tk.Tk):
    """
    Main application window.
    """

    def __init__(self) -> None:
        super().__init__()

        self.config: dict = load_config()

        self.language: str = self.config.get("language", "en-US")

        self.i18n: I18nManager = I18nManager(language=self.language)

        self.flag_icons = {
            "pt-BR": tk.PhotoImage(file=resource_path(r"assets\br_icon.png")),
            "en-US": tk.PhotoImage(file=resource_path(r"assets\us_icon.png")),
        }

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
        self.geometry("850x500")
        self.minsize(850, 500)

        set_window_icon(self)

        self.theme: str = self.config.get("theme", "light")

        self.pause_resume_button: ttk.Button = None
        self.cancel_button: ttk.Button = None

        self._ckb_bg = None
        self._ckb_fg = None
        self._ckb_active_bg = None
        self._ckb_indicator_bg = None
        self._ckb_indicator_fg = None
        self._ckb_selectcolor = None

        self.status_var: tk.StringVar = tk.StringVar(value=self.i18n.t("ready"))
        self.progress_var: tk.DoubleVar = tk.DoubleVar(value=0)
        self.saved_selection: dict = None
        self.selected_resolution: tk.StringVar = tk.StringVar(value="Auto")
        self._configure_style()
        self._build_ui()
        self._apply_theme()

        self._update_resolution_state()

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
            resume: bool = ThemedMessageBox.ask_yes_no(
                parent=self,
                title=self.i18n.t("app.window.state_to_resume_title"),
                message=self.i18n.t("app.window.state_to_resume"),
                theme=self.get_theme_context()
            )

            if resume:
                # Marks that the app is resuming from a crash
                self._resume_from_state(self.STATE_FILE)

            else:
                # User chose not to resume → cleanup
                self._on_no_resume()

        self.protocol("WM_DELETE_WINDOW", self.on_window_close)

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
        self.help_btn: ttk.Button = ttk.Button(
            header,
            text="❔",
            width=3,
            command=self._open_help
        )
        self.help_btn.configure(takefocus=False)
        self.help_btn.pack(side="right", padx=(5, 0))

        Tooltip(self.help_btn, self.i18n.t("help"))

        # Langauge toggle button
        self.lang_btn = ttk.Button(
            header,
            image=self.flag_icons[self.language],
            width=3,
            command=self.on_language_clicked
        )
        self.lang_btn.pack(side="right", padx=(5, 0))
        self.lang_btn.configure(takefocus=False)

        Tooltip(self.lang_btn, self.i18n.t("lang"))

        # Theme toggle button
        self.theme_btn: ttk.Button = ttk.Button(
            header,
            text="🌙",
            width=3,
            command=self.toggle_theme
        )
        self.theme_btn.configure(takefocus=False)
        self.theme_btn.pack(side="right",padx=(5, 0))

        Tooltip(self.theme_btn, self.i18n.t("theme"))

    def _build_url_section(self) -> None:
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame, text=self.i18n.t("url")).grid(
            row=0, column=0, columnspan=3, sticky="w"
        )

        self.url_entry = ttk.Entry(frame)
        self.url_entry.grid(
            row=1, column=0, sticky="ew", padx=(0, 5)
        )

        paste_btn = ttk.Button(
            frame,
            text="📋",
            width=4,
            command=self._paste_url
        )
        paste_btn.configure(takefocus=False)
        paste_btn.grid(row=1, column=1)

        Tooltip(paste_btn, self.i18n.t("paste"))

        # Layout rules
        frame.columnconfigure(0, weight=1)

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
        ttk.Label(frame, text=self.i18n.t("audio_format_label")).pack(side="left")

        format_options: list = ["mp3", "wav", "flac", "m4a"]

        self.audio_format_menu: ttk.Combobox = ttk.Combobox(
            frame,
            textvariable=self.audio_format_var,
            values=format_options,
            width=5,
            state="readonly"
        )
        self.audio_format_menu.pack(side="left", padx=(5, 15))

        Tooltip(self.audio_format_menu, self.i18n.t("audio_format"))

        # -------------------------
        # Audio Quality
        # -------------------------
        ttk.Label(frame, text=self.i18n.t("audio_quality_label")).pack(side="left", padx=(0, 5))

        quality_options: list = ["128", "192", "256", "320"]

        self.audio_quality_menu: ttk.Combobox = ttk.Combobox(
            frame,
            textvariable=self.audio_quality_var,
            values=quality_options,
            width=7,
            state="readonly"
        )
        self.audio_quality_menu.pack(side="left", padx=(5, 15))

        Tooltip(self.audio_quality_menu, self.i18n.t("audio_quality"))

        # -------------------------
        # Checkbuttons for extra options
        # -------------------------
        self.playlist_ckb = tk.Checkbutton(
            frame,
            text=self.i18n.t("playlist"),
            variable=self.playlist_var
        )
        self.playlist_ckb.pack(side="left", padx=(0, 10))
        self.style_tk_checkbutton(self.playlist_ckb)

        self.normalize_ckb: tk.Checkbutton = tk.Checkbutton(
            frame,
            text=self.i18n.t("normalize_audio"),
            variable=self.normalize_var
        )
        self.normalize_ckb.pack(side="left", padx=(0, 10))
        self.style_tk_checkbutton(self.normalize_ckb)

        Tooltip(self.normalize_ckb, self.i18n.t("normalize_ckb"))

        self.keep_original_ckb: tk.Checkbutton = tk.Checkbutton(
            frame,
            text=self.i18n.t("keep_original"),
            variable=self.keep_original_var,
            command=self._update_resolution_state
        )
        self.keep_original_ckb.pack(side="left", padx=(0, 10))
        self.style_tk_checkbutton(self.keep_original_ckb)

        Tooltip(self.keep_original_ckb, self.i18n.t("keep_original_ckb"))

        ttk.Label(frame, text=self.i18n.t("resolution_label")).pack(side="left", padx=(0, 5))

        self.resolution_cb = ttk.Combobox(
            frame,
            textvariable=self.selected_resolution,
            values=["Auto", "480p", "720p", "1080p"],
            state="readonly",
            width=10
        )
        self.resolution_cb.pack(side="left", padx=(5, 15))

        Tooltip(self.resolution_cb, self.i18n.t("video_resolution"))

        self.resolution_cb.bind(
            "<<ComboboxSelected>>",
            lambda e: self._on_resolution_change()
        )

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
            text=self.i18n.t("download"),
            command=self.start_download
        )
        self.download_btn.configure(takefocus=False)
        self.download_btn.pack(side="left", padx=(5, 0))

        Tooltip(self.download_btn, self.i18n.t("download_btn"))

        self.pause_resume_btn: ttk.Button = ttk.Button(
            frame,
            text=self.i18n.t("pause"),
            command=self.on_pause_resume_clicked,
            state="disabled"
        )
        self.pause_resume_btn.configure(takefocus=False)
        self.pause_resume_btn.pack(side="left", padx=(5, 0))

        Tooltip(self.pause_resume_btn, self.i18n.t("pause_resume_btn"))

        self.cancel_btn: ttk.Button = ttk.Button(
            frame,
            text=self.i18n.t("cancel"),
            command=self.on_cancel_clicked,
            state="disabled"
        )
        self.pause_resume_btn.configure(takefocus=False)
        self.cancel_btn.pack(side="left", padx=(5, 0))

        Tooltip(self.cancel_btn, self.i18n.t("cancel_btn"))

        self.open_btn: ttk.Button = ttk.Button(
            frame,
            text=self.i18n.t("open_label"),
            command=self._open_folder)
        self.open_btn.configure(takefocus=False)
        self.open_btn.pack(side="left", padx=(5, 0))

        Tooltip(self.open_btn, self.i18n.t("open"))

    def _build_save_folder(self) -> None:
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame, text=self.i18n.t("save_in_label")).grid(
            row=0, column=0, columnspan=3, sticky="w"
        )

        self.output_entry = ttk.Entry(
            frame,
            textvariable=self.output_path_var
        )
        self.output_entry.grid(
            row=1, column=0, sticky="ew", padx=(0, 5)
        )

        choose_btn = ttk.Button(
            frame,
            text=self.i18n.t("choose_label"),
            width=10,
            command=self._choose_folder
        )
        choose_btn.configure(takefocus=False)
        choose_btn.grid(row=1, column=1)

        Tooltip(choose_btn, self.i18n.t("choose"))

        frame.columnconfigure(0, weight=1)

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

        # ===============================
        # Show / hide log checkbox
        # ===============================
        self.show_log_var = tk.BooleanVar(value=True)

        chk: tk.Checkbutton = tk.Checkbutton(
            container,
            text=self.i18n.t("show_log"),
            variable=self.show_log_var,
            command=self._toggle_log
        )
        chk.pack(anchor="w")
        self.style_tk_checkbutton(chk)

        # ===============================
        # Log area with scrollbar
        # ===============================
        log_frame = ttk.Frame(container)
        log_frame.pack(fill="both", expand=True, pady=(5, 0))

        scrollbar = ttk.Scrollbar(log_frame, orient="vertical")

        self.log_text: tk.Text = tk.Text(
            log_frame,
            height=10,
            state="disabled",
            yscrollcommand=scrollbar.set,
            wrap="word"
        )

        scrollbar.config(command=self.log_text.yview)

        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ===============================
        # Mouse wheel support
        # ===============================
        self.log_text.bind("<Enter>", lambda _: self.log_text.bind_all(
            "<MouseWheel>", self._on_log_mousewheel
        ))
        self.log_text.bind("<Leave>", lambda _: self.log_text.unbind_all(
            "<MouseWheel>"
        ))

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

        config = load_config()
        config["theme"] = self.theme
        save_config(config)

        if self.theme == "dark":
            bg = "#1e1e1e"
            fg = "#ffffff"
            entry_bg = "#2e2e2e"
            entry_fg = "#ffffff"
            btn_bg = "#3a3a3a"
            btn_fg = "#ffffff"
            btn_hover_bg = "#505050"
            ckb_bg = bg
            ckb_fg = fg
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

        self.bg = bg
        self.fg = fg
        self.entry_bg = entry_bg
        self.entry_fg = entry_fg
        self.btn_bg = btn_bg
        self.btn_fg = btn_fg

        self._ckb_bg = ckb_bg
        self._ckb_fg = ckb_fg
        self._ckb_active_bg = ckb_hover_bg
        self._ckb_indicator_bg = entry_bg
        self._ckb_indicator_fg = fg
        self._ckb_selectcolor = entry_bg

        # Main window background
        self.configure(bg=bg)

        # Configure ttk styles
        style = self.style
        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure(
            "TEntry",
            fieldbackground=entry_bg,
            foreground=entry_fg,
            background=entry_bg
        )
        style.map(
            "TEntry",
            fieldbackground=[("readonly", entry_bg)],
            foreground=[("readonly", entry_fg)]
        )
        style.configure("TButton", background=btn_bg, foreground=btn_fg)
        style.map(
            "TButton",
            background=[("active", btn_hover_bg)],
            foreground=[("active", btn_fg)]
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

                except tk.TclError:
                    pass
                _recursive_apply(child)

        _recursive_apply(self)

        def _reapply_checkbuttons(widget):
            for child in widget.winfo_children():
                if isinstance(child, tk.Checkbutton):
                    self.style_tk_checkbutton(child)
                _reapply_checkbuttons(child)

        _reapply_checkbuttons(self)

    def style_tk_checkbutton(self, chk: tk.Checkbutton) -> None:
        chk.configure(
            background=self._ckb_bg,
            foreground=self._ckb_fg,
            activebackground=self._ckb_active_bg,
            activeforeground=self._ckb_fg,
            selectcolor=self._ckb_selectcolor,
            indicatoron=True,
            highlightthickness=0,
            bd=0,
            relief="flat",
            anchor="w",
            justify="left",
            takefocus=False
        )

    # =========================
    # Download
    # =========================
    def start_download(self) -> None:
        url: str = self.url_entry.get().strip()

        if not self._validate_url(url):
            return

        self.set_downloading_state()

        self.progress_var.set(0)
        self.status_var.set(self.i18n.t("initiating"))

        Thread(target=self.run_download, daemon=True).start()

    def run_download(self) -> None:
        os.makedirs(self.output_path_var.get(), exist_ok=True)

        options: dict = {
            "output_path": self.output_path.strip(),
            "audio_format": self.audio_format_var.get(),
            "audio_quality": self.audio_quality_var.get(),
            "video_resolution": self.selected_resolution.get(),
            "allow_playlist": self.playlist_var.get(),
            "keep_original": self.keep_original_var.get(),
            "normalize_enabled": self.normalize_var.get(),
            "progress_hook": self.on_progress,
            "status_hook": self.set_status,
            "file_finished_hook": self.on_file_finished,
            "error_hook": self.on_error,
            "log_hook": self._log,
            "state_file": self.STATE_FILE,
            "playlist_selection": self.saved_selection,
            "language": self.language
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

        if "level" not in message:
            entry: str = f"[{timestamp}] {level}: {message}\n"

        else:
            entry: str = message

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
            self._log(self.i18n.t("app.window.log_validate_url"), level=self.i18n.t("error_level"))
            self._show_error(self.i18n.t("app.window.error_log_validate_not_url"))

            return False

        if not self._looks_like_youtube_url(url):
            self._log(f"{self.i18n.t('app.window.error_log_not_looks_url')} {url}", level=self.i18n.t("error_level"))
            self._show_error(self.i18n.t("app.window.error_log_not_looks_url"))

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


    def _show_error(self, message: str) -> None:
        """
        Display an error message dialog to the user.

        Args:
            message (str): Error message to display.
        """

        ThemedMessageBox.show_error(
            parent=self,
            title=self.i18n.t("error"),
            message=message,
            theme=self.get_theme_context()
        )

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

    def on_pause_resume_clicked(self) -> None:
        if not self.is_paused:
            # Pause
            self.controller.pause()
            self.is_paused = True
            self.pause_resume_btn.config(text=self.i18n.t("resume"))

        else:
            # Resume
            self.controller.resume()
            self.is_paused = False
            self.pause_resume_btn.config(text=self.i18n.t("pause"))

    def on_cancel_clicked(self) -> None:
        if not hasattr(self, "controller") or not self.controller:
            return

        # Playlist
        if self.playlist_var.get():
            confirm = ThemedMessageBox.ask_yes_no(
                parent=self,
                title=self.i18n.t("app.window.on_cancel_clicked_title"),
                message=self.i18n.t("app.window.on_cancel_clicked"),
                theme=self.get_theme_context()
            )

            if not confirm:
                return

            self.controller.cancel(after_current=True)

            self.status_var.set(self.i18n.t("app.window.status_on_cancel_clicked_playlist"))
            self._log(
                self.i18n.t("app.window.log_on_cancel_clicked_playlist"),
                level=self.i18n.t("cancel_level")
            )

        # Single
        else:
            self.controller.cancel(after_current=False)

            self.status_var.set(self.i18n.t("app.window.status_on_cancel_clicked_single"))
            self._log(self.i18n.t("app.window.log_on_cancel_clicked_single"), level=self.i18n.t("cancel_level"))

        self.cancel_btn.config(state="disabled")

    def _resume_from_state(self, path: str) -> None:
        import json

        if not os.path.exists(path):
            return

        with open(path, "r", encoding="utf-8") as f:
            state = json.load(f)

        # ===============================
        # Restore basic fields
        # ===============================
        url: str = state.get("url", "")

        self.url_entry.delete(0, "end")

        if isinstance(url, str) and url.strip():
            self.url_entry.insert(0, url)

        else:
            self.url_entry.delete(0, "end")

        self.audio_format_var.set(state.get("audio_format", "mp3"))
        self.audio_quality_var.set(state.get("quality", "192"))
        self.playlist_var.set(state.get("allow_playlist", False))
        self.keep_original_var.set(state.get("keep_original", False))
        self.normalize_var.set(state.get("normalize_enabled", False))
        self.output_path_var.set(state.get("output_path", download_dir))
        self.selected_resolution.set(state.get("resolution", "Auto"))

        self.saved_selection = state.get("playlist_selection")

        paused: bool = state.get("paused", False)
        mode: str = state.get("mode", "single")

        print(mode)

        # ===============================
        # Decide resume behavior
        # ===============================
        if not paused:
            print(paused)
            # 🔥 NEVER auto-start if not paused
            return

        # ===============================
        # Resume logic by mode
        # ===============================
        if mode == "single":
            self.start_download()

        elif mode == "playlist":
            self.start_download()

        else:
            # Unknown mode → safest behavior
            return

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
        self._log(self.i18n.t("app.window.log_on_no_resume"))

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
                text: str = f"{self.i18n.t('status.progress')} {percent:.1f}%"
                if item_index and total_items:
                    text: str = f"{self.i18n.t('status.index')} {item_index}/{total_items} — {text}"
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
            self._log(f"{self.i18n.t('app.window.log_on_file_finished')} {os.path.basename(filename)}")
            self.progress_var.set(0)

        self.after(0, update)

    def on_error(self, message) -> None:
        """
        Log the error that occurred.

        :param message: Error message.
        :type message: str
        """
        self.after(0, lambda: ThemedMessageBox.show_error(
            parent=self,
            title=self.i18n.t("error"),
            message=message,
            theme=self.get_theme_context()
        ))

    def show_mix_warning(self) -> None:
        """
        Displays a warning message explaining that YouTube MIX playlists
        cannot be downloaded as regular playlists.
        """
        ThemedMessageBox.show_warning(
            parent=self,
            title=self.i18n.t("app.window.show_mix_warming_title"),
            message=self.i18n.t("app.window.show_mix_warming"),
            theme=self.get_theme_context()
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
        self.pause_resume_btn.config(text=self.i18n.t("pause"), state="disabled")
        self.cancel_btn.config(state="disabled")
        self.is_paused = False
        self.status_var.set(self.i18n.t("ready"))

    def set_downloading_state(self) -> None:
        """
        Set the UI to the downloading state.

        Disables the download button, enables pause/resume and cancel buttons,
        and ensures the paused flag is reset.
        """

        self.download_btn.config(state="disabled")
        self.pause_resume_btn.config(text=self.i18n.t("pause"), state="normal")
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

    def _on_resolution_change(self):
        self.selected_resolution.set(self.resolution_cb.get())

    def _update_resolution_state(self) -> None:
        """

        :return:
        """
        can_select_resolution: bool = self.keep_original_var.get()

        if can_select_resolution:
            self.resolution_cb.configure(state="readonly")

        else:
            self.selected_resolution.set("Auto")
            self.resolution_cb.config(state="disabled")

    def on_language_clicked(self) -> None:
        new_lang = "pt-BR" if self.language == "en-US" else "en-US"

        config = load_config()
        config["language"] = new_lang
        config["theme"] = self.theme
        save_config(config)

        self._show_restart_dialog()

    def _show_restart_dialog(self) -> None:
        result = ThemedMessageBox.ask_yes_no(
            parent=self,
            title=self.i18n.t("app.window.show_restart_title"),
            message=self.i18n.t("app.window.show_restart"),
            theme=self.get_theme_context()
        )

        if result:
            self._restart_app()

    def _restart_app(self, dialog=None):
        if dialog:
            dialog.destroy()

        self.update_idletasks()
        self.destroy()

        if getattr(sys, "frozen", False):
            # Packaged app (PyInstaller / cx_Freeze)
            subprocess.Popen(
                [sys.executable],
                close_fds=True,
                shell=False
            )
        else:
            # Development mode
            main_file = os.path.abspath(sys.modules["__main__"].__file__)
            subprocess.Popen(
                [sys.executable, main_file],
                close_fds=True,
                shell=False
            )

        sys.exit(0)

    def _open_help(self):
        HelpWindow(
            parent=self,
            help_text=self.i18n.help_text("HELP_TEXT"),
            theme={
                "bg": self.bg,
                "fg": self.fg,
                "accent": "#4ea1ff",
                "warning": "#ff6b6b"
            }
        )

    def get_theme_context(self) -> dict:
        theme: dict = {
            "bg": self.bg,
            "fg": self.fg,
            "accent": "#4ea1ff",
            "warning": "#ff6b6b"
        }

        return theme

    def _on_log_mousewheel(self, event):
        self.log_text.yview_scroll(int(-1 * (event.delta / 120)), "units")
