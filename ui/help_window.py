import tkinter as tk
from tkinter import ttk
import webbrowser


class HelpWindow(tk.Toplevel):
    def __init__(self, parent, help_text: dict):
        super().__init__(parent)

        self.title(help_text["title"])
        self.geometry("650x720")
        self.resizable(False, True)
        self.transient(parent)
        self.grab_set()

        container = ttk.Frame(self, padding=15)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        content = ttk.Frame(canvas)

        content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ===== HEADER =====
        ttk.Label(
            content,
            text=help_text["header"],
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", pady=(0, 10))

        ttk.Label(
            content,
            text=help_text["intro"],
            wraplength=600,
            justify="left"
        ).pack(anchor="w", pady=(0, 15))

        self._section(content, help_text["features_title"], help_text["features"])
        self._section(content, help_text["usage_title"], help_text["usage"])
        self._section(content, help_text["tips_title"], help_text["tips"])

        ttk.Label(
            content,
            text=help_text["restart_note"],
            wraplength=600,
            foreground="#aa0000"
        ).pack(anchor="w", pady=(15, 20))

        ttk.Separator(content).pack(fill="x", pady=10)

        # ===== GITHUB =====
        git_frame = ttk.Frame(content)
        git_frame.pack(anchor="w")

        ttk.Label(git_frame, text=help_text["git_label"]).pack(side="left")

        link = ttk.Label(
            git_frame,
            text=help_text["git_url"],
            foreground="#0066cc",
            cursor="hand2"
        )
        link.pack(side="left", padx=5)

        link.bind(
            "<Button-1>",
            lambda _: webbrowser.open(help_text["git_url"])
        )

        ttk.Button(content, text="OK", command=self.destroy).pack(pady=20)

    @staticmethod
    def _section(parent, title, items):
        ttk.Label(
            parent,
            text=title,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(10, 5))

        for item in items:
            ttk.Label(
                parent,
                text=item,
                wraplength=600,
                justify="left"
            ).pack(anchor="w")
