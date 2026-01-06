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
from typing import List, Dict, Any, Optional

from utils.helpers import duration_format

class PlaylistFrame(tk.Toplevel):
    """
    Modal window used to select which videos from a YouTube playlist
    should be downloaded.

    This window does NOT perform any download logic.
    It only returns the selected playlist entries.
    """

    def __init__(
        self,
        master: tk.Widget,
        playlist_title: str,
        entries: List[Dict[str, Any]],
        theme: str = "light"
    ) -> None:
        super().__init__(master)

        self.title("Select playlist videos")
        self.geometry("550x400")

        self.theme: str = theme

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

        self.inner_frame: ttk.Frame = ttk.Frame(self.canvas)

        self.inner_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._populate_entries()

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
            bg = "#2b2b2b"
            fg = "#ffffff"
            disabled_fg = "#888888"
            hover_bg = "#3a3a3a"
            scrollbar_bg = "#3a3a3a"
            trough_bg = "#2b2b2b"
        else:
            bg = "#f5f5f5"
            fg = "#000000"
            disabled_fg = "#888888"
            hover_bg = "#e6e6e6"
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
            "Playlist.TCheckbutton",
            background=bg,
            foreground=fg
        )

        style.map(
            "Playlist.TCheckbutton",
            background=[("active", hover_bg)],
            foreground=[("disabled", disabled_fg)]
        )

        style.configure(
            "Vertical.TScrollbar",
            background=scrollbar_bg,
            troughcolor=trough_bg
        )

    def _populate_entries(self) -> None:
        """
        Populate the playlist entries with checkbuttons.
        """

        self.check_buttons: list = []

        for index, entry in enumerate(self.entries, start=1):
            already_downloaded: bool = entry.get("_already_downloaded", False)
            preselected: bool = entry.get("__preselected__", False)

            var: tk.BooleanVar = tk.BooleanVar(value=preselected)

            title: str = entry.get("title", "untitled")
            duration: float = entry.get("duration", 0)
            duration_str: str = duration_format(duration)

            label: str = f"{index}. {title} [{duration_str}]"

            if already_downloaded:
                label: str = f"✔ {label} (already downloaded)"

            chk: tk.Checkbutton = tk.Checkbutton(
                self.inner_frame,
                text=label,
                variable=var,
                anchor="w",
                justify="left",
                wraplength=500,
                fg="gray" if already_downloaded else "black",
                state="disabled" if already_downloaded else "normal"
            )

            chk.pack(fill="x", anchor="w", pady=2)

            self.check_vars.append(var)
            self.check_buttons.append(chk)

    def _build_buttons(self, parent: ttk.Frame) -> None:
        """
        Build footer action buttons.
        """

        ttk.Button(parent, text="Select all", command=self.select_all).pack(side="left", padx=(0, 5))
        ttk.Button(parent, text="Deselect all", command=self.deselect_all).pack(side="left", padx=(0, 20))

        ttk.Button(parent, text="Download", command=self.on_confirm).pack(side="left")
        ttk.Button(parent, text="Cancel", command=self.on_cancel).pack(side="left", padx=(5, 0))

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
            if var.get():
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
