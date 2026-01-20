# ui/playlist_frame.py

"""
Playlist Selection Window
-------------------------

This module provides a modal window that allows the user to select
which videos from a YouTube playlist should be downloaded.

Features:
- Scrollable list of playlist entries
- Detection of already downloaded items
- Select all / deselect all actions
- Light and dark theme support
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ui.app_window import AppWindow

from utils.helpers import duration_format
from ui.tooltip import Tooltip
from utils.window import center_window, set_window_icon


class PlaylistFrame(tk.Toplevel):
    """
    Modal window used to select which videos from a YouTube playlist
    should be downloaded.

    This window does NOT perform any download logic.
    It only returns the selected playlist entries.
    """

    def __init__(
        self,
        master: "AppWindow",
        playlist_title: str,
        entries: List[Dict[str, Any]],
        theme: str = "light"
    ) -> None:
        super().__init__(master)

        self.app: AppWindow = master

        # self.i18n: I18nManager = I18nManager(language="en-US")

        self.title("Select playlist videos")
        self.geometry("850x500")
        set_window_icon(self)

        self.theme: str = theme

        center_window(self, master)

        self.entries: List[Dict[str, Any]] = list(entries)
        self.check_vars: List[tk.BooleanVar] = []
        self.check_buttons: List[tk.Checkbutton] = []

        self.selected: Optional[List[Dict[str, Any]]] = None

        # Header
        ttk.Label(
            self,
            text=f"Playlist: {playlist_title}",
            font=("TkDefaultFont", 12, "bold")
        ).pack(anchor="w", padx=10, pady=5)

        # Scrollable area
        container: ttk.Frame = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=10, pady=5)

        self.canvas: tk.Canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar: ttk.Scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)

        self.inner_frame: tk.Frame = tk.Frame(self.canvas)

        self.inner_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

        self._populate_entries()

        self._apply_theme()

        # Footer buttons
        footer: ttk.Frame = ttk.Frame(self)
        footer.pack(fill="x", padx=10, pady=(5, 10))

        self._build_buttons(footer)

        # Modal behavior
        self.grab_set()
        self.focus_set()
        self.transient(master)

        # UX improvement: auto-scroll to first not downloaded video
        self.after(100, self._scroll_to_first_pending)

    def _apply_theme(self) -> None:
        """
        Apply light or dark theme colors to the playlist window.
        """
        if self.theme == "dark":
            bg = "#1e1e1e"
            # fg = "#ffffff"
            # selectcolor = "#2e2e2e"
            # disabled_fg = "#888888"
            # hover_bg = "#3a3a3a"
            scrollbar_bg = "#3a3a3a"
            trough_bg = "#2b2b2b"
        else:
            bg = "#f5f5f5"
            # fg = "#000000"
            # selectcolor = "#ffffff"
            # disabled_fg = "#888888"
            # hover_bg = "#e6e6e6"
            scrollbar_bg = "#e0e0e0"
            trough_bg = "#f5f5f5"

        # Window + containers
        self.configure(bg=bg)
        self.canvas.configure(bg=bg)
        self.inner_frame.configure(bg=bg)

        # ttk styles
        style = ttk.Style(self)
        style.theme_use("default")

        style.configure(
            "Vertical.TScrollbar",
            background=scrollbar_bg,
            troughcolor=trough_bg
        )

    def _populate_entries(self) -> None:
        """
        Populate the playlist entries with checkbuttons
        and visual restriction badges.
        """

        self.check_buttons: list = []
        self.check_vars: list = []

        for index, entry in enumerate(self.entries, start=1):
            already_downloaded: bool = entry.get("_already_downloaded", False)
            preselected: bool = entry.get("__preselected__", False)

            restricted: str | None = entry.get("__restricted__")

            var: tk.BooleanVar = tk.BooleanVar(value=preselected)

            title: str = entry.get("title", "untitled")
            raw_duration = entry.get("duration")

            if raw_duration is None:
                duration_str: str = "—:—"
            else:
                duration_str: str = duration_format(raw_duration)

            # ============================
            # Restriction badge
            # ============================
            badge = ""
            if restricted == "private":
                badge = " 🔒 Private"
            elif restricted == "age":
                badge = " 🔞 Age"

            label = f"{index}. {title} [{duration_str}]{badge}"

            if already_downloaded:
                label = f"✔ {label} (already downloaded)"

            chk = tk.Checkbutton(
                self.inner_frame,
                text=label,
                variable=var,
                anchor="w",
                justify="left",
                wraplength=750
            )

            self.app.style_tk_checkbutton(chk)

            if already_downloaded:
                chk.configure(fg="#888888")

            chk.pack(
                fill="x",
                anchor="w",
                padx=(2, 4),
                pady=2
            )

            self.check_vars.append(var)
            self.check_buttons.append(chk)

    def _build_buttons(self, parent: ttk.Frame) -> None:
        """
        Build footer action buttons.
        """

        select_all_btn: ttk.Button = ttk.Button(parent, text=self.app.i18n.t("playlist_frame.select_all_btn_label"), command=self.select_all)
        select_all_btn.pack(side="left", padx=(0, 5))
        select_all_btn.configure(takefocus=False)

        Tooltip(select_all_btn, self.app.i18n.t("playlist_frame.select_all_btn"))

        deselect_all_btn: ttk.Button = ttk.Button(parent, text=self.app.i18n.t("playlist_frame.deselect_all_btn_label"), command=self.deselect_all)
        deselect_all_btn.pack(side="left", padx=(0, 20))
        deselect_all_btn.configure(takefocus=False)

        Tooltip(deselect_all_btn, self.app.i18n.t("playlist_frame.deselect_all_btn"))

        download_btn: ttk.Button = ttk.Button(parent, text=self.app.i18n.t("playlist_frame.download_btn_label"), command=self.on_confirm)
        download_btn.pack(side="left")
        download_btn.configure(takefocus=False)

        Tooltip(download_btn, self.app.i18n.t("playlist_frame.download_btn"))

        cancel_btn: ttk.Button = ttk.Button(parent, text=self.app.i18n.t("playlist_frame.cancel_btn_label"), command=self.on_cancel)
        cancel_btn.pack(side="left", padx=(5, 0))
        cancel_btn.configure(takefocus=False)

        Tooltip(cancel_btn, self.app.i18n.t("playlist_frame.cancel_btn"))

    def select_all(self) -> None:
        """
        Select all non-disabled videos.
        """

        for var, chk in zip(self.check_vars, self.check_buttons):
            if chk.cget("state") != "disabled":
                var.set(True)

    def deselect_all(self) -> None:
        """
        Deselect all non-disabled videos.
        """

        for var, chk in zip(self.check_vars, self.check_buttons):
            if chk.cget("state") != "disabled":
                var.set(False)

    def on_confirm(self) -> None:
        """
        Confirm selection and close the window.
        """

        self.selected: List[Dict[str, Any]] = self.get_selected_entries()
        self.destroy()

    def on_cancel(self) -> None:
        """
        Cancel selection and close the window.
        """

        self.selected = None
        self.destroy()

    def get_selected_entries(self) -> List[Dict[str, Any]]:
        """
        Return all selected playlist entries.

        Returns:
            List[Dict[str, Any]]: selected playlist entries
        """

        selected: List[Dict[str, Any]] = []

        for var, entry in zip(self.check_vars, self.entries):
            if not var.get():
                continue

            if entry.get("__restricted__"):
                continue

            if entry.get("_already_downloaded"):
                continue

            selected.append(entry)

        return selected

    def _scroll_to_first_pending(self) -> None:
        """
        Automatically scroll to the first video that is not downloaded.
        """

        for chk in self.check_buttons:
            if chk.cget("state") != "disabled":
                self.canvas.yview_moveto(
                    chk.winfo_y() / max(1, self.inner_frame.winfo_height())
                )
                break

    def _on_mousewheel(self, event: tk.Event) -> None:
        scroll_region = self.canvas.bbox("all")
        if not scroll_region:
            return

        content_height = scroll_region[3] - scroll_region[1]
        canvas_height = self.canvas.winfo_height()

        if content_height <= canvas_height:
            return

        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind_mousewheel(self, event: tk.Event) -> None:
        _e = event
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event: tk.Event) -> None:
        _e = event
        self.canvas.unbind_all("<MouseWheel>")

    def destroy(self):
        self.unbind_all("<MouseWheel>")
        super().destroy()
