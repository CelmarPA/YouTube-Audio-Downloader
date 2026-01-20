# ui/help_window.py

import tkinter as tk
import webbrowser

from tkinter import ttk

from utils.window import center_window, set_window_icon


class HelpWindow(tk.Toplevel):
    def __init__(self, parent, help_text: dict, theme: dict):
        super().__init__(parent)

        self.theme = theme

        self.title(help_text["title"])
        self.geometry("650x720")
        set_window_icon(self)
        self.resizable(False, True)
        self.transient(parent)
        self.grab_set()
        self.configure(bg=theme["bg"])

        center_window(self, parent)

        # ===============================
        # Styles (isolated & safe)
        # ===============================
        style = ttk.Style(self)

        style.configure(
            "HelpTitle.TLabel",
            font=("Segoe UI", 16, "bold"),
            background=theme["bg"],
            foreground=theme["fg"]
        )

        style.configure(
            "HelpSection.TLabel",
            font=("Segoe UI", 12, "bold"),
            background=theme["bg"],
            foreground=theme["fg"]
        )

        style.configure(
            "HelpText.TLabel",
            background=theme["bg"],
            foreground=theme["fg"]
        )

        style.configure(
            "HelpLink.TLabel",
            background=theme["bg"],
            foreground=theme["accent"]
        )

        style.configure(
            "HelpWarning.TLabel",
            background=theme["bg"],
            foreground=theme["warning"]
        )

        # ===============================
        # Layout with scroll
        # ===============================
        container = ttk.Frame(self, padding=15)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            container,
            bg=theme["bg"],
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            container,
            orient="vertical",
            command=self.canvas.yview
        )

        content = ttk.Frame(self.canvas)

        content.bind(
            "<Configure>",
            lambda _: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window(
            (0, 0),
            window=content,
            anchor="nw"
        )

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ===============================
        # Mouse wheel support
        # ===============================
        self.bind("<Enter>", self._bind_mousewheel)
        self.bind("<Leave>", self._unbind_mousewheel)

        # ===============================
        # HEADER
        # ===============================
        ttk.Label(
            content,
            text=help_text["header"],
            style="HelpTitle.TLabel"
        ).pack(anchor="w", pady=(0, 10))

        ttk.Label(
            content,
            text=help_text["intro"],
            wraplength=600,
            justify="left",
            style="HelpText.TLabel"
        ).pack(anchor="w", pady=(0, 15))

        self._section(
            content,
            help_text["features_title"],
            help_text["features"]
        )

        self._section(
            content,
            help_text["usage_title"],
            help_text["usage"]
        )

        self._section(
            content,
            help_text["tips_title"],
            help_text["tips"]
        )

        # ===============================
        # Restart note
        # ===============================
        ttk.Label(
            content,
            text=help_text["restart_note"],
            wraplength=600,
            style="HelpWarning.TLabel"
        ).pack(anchor="w", pady=(15, 20))

        ttk.Separator(content).pack(fill="x", pady=10)

        # ===============================
        # GitHub link
        # ===============================
        git_frame = ttk.Frame(content)
        git_frame.pack(anchor="w")

        ttk.Label(
            git_frame,
            text=help_text["git_label"],
            style="HelpText.TLabel"
        ).pack(side="left")

        link = ttk.Label(
            git_frame,
            text=help_text["git_url"],
            style="HelpLink.TLabel",
            cursor="hand2"
        )
        link.pack(side="left", padx=5)

        link.bind(
            "<Button-1>",
            lambda _: webbrowser.open(help_text["git_url"])
        )

        # ===============================
        # OK button
        # ===============================
        ttk.Button(
            content,
            text="OK",
            command=self.destroy
        ).pack(pady=20)



    # ===============================
    # Sections helper
    # ===============================
    @staticmethod
    def _section(parent, title, items):
        ttk.Label(
            parent,
            text=title,
            style="HelpSection.TLabel"
        ).pack(anchor="w", pady=(10, 5))

        for item in items:
            ttk.Label(
                parent,
                text=item,
                wraplength=600,
                justify="left",
                style="HelpText.TLabel"
            ).pack(anchor="w")

    # ===============================
    # Mouse wheel handlers
    # ===============================
    def _bind_mousewheel(self, _=None):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, _=None):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )
