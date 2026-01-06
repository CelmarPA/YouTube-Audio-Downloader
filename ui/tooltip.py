# ui/tooltip.py

"""
Tooltip Widget
--------------

Provides a reusable tooltip component for Tkinter widgets.
The tooltip appears after a configurable delay when the user
hovers over a widget and disappears when the cursor leaves.

Designed to be lightweight, theme-agnostic, and easy to attach
to any Tkinter or ttk widget.
"""

import tkinter as tk

from tkinter import ttk
from typing import Optional


class Tooltip:
    """Tooltip widget with delayed hover display."""

    def __init__(self, widget: tk.Widget, text: str, delay: int = 1500) -> None:
        self.widget = widget
        self.text = text
        self.delay = delay
        self._after_id: Optional[str] = None
        self.tip_window: Optional[tk.Toplevel] = None

        widget.bind("<Enter>", self._schedule)
        widget.bind("<Leave>", self._hide)

    def _schedule(self, _: tk.Event) -> None:
        self._after_id = self.widget.after(
            self.delay,
            lambda *_: self._show()
        )

    def _show(self) -> None:
        if self.tip_window:
            return

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20

        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.overrideredirect(True)
        self.tip_window.geometry(f"+{x}+{y}")

        label: ttk.Label = ttk.Label(
            self.tip_window,
            text=self.text,
            background="#333",
            foreground="#fff",
            padding=6,
            wraplength=250
        )
        label.pack()

    def _hide(self, _: tk.Event) -> None:
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None

        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None
