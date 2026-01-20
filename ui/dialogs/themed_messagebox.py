# ui/dialogs/themed_messagebox.py

"""
Custom themed message box dialogs using Tkinter.

This module provides a reusable, theme-aware message box implementation
with support for yes/no questions, warnings, errors, and informational dialogs.
"""

import tkinter as tk

from tkinter import ttk
from functools import partial
from typing import Any

from utils.app_config import load_config
from i18n.manager import I18nManager
from utils.window import center_window, set_window_icon

# Default dialog dimensions
WIDTH = 460
HEIGHT = 220

# Default button width
BTN_WIDTH = 12


# Load application configuration
config: dict = load_config()

# Current language setting
language: str = config.get("language", "en-US")

# Internationalization manager
i18n: I18nManager = I18nManager(language=language)


class ThemedMessageBox:
    """
    Provides themed modal message dialogs.

    This class centralizes the creation of message boxes with consistent
    styling, localization support, and modal behavior.
    """

    @staticmethod
    def _base_dialog(
        *,
        parent=None,
        title: str,
        message: str,
        theme: dict,
        buttons: tuple
    ) -> bool | None:
        """
        Create and display a modal themed dialog window.

        :param parent: Parent window for modal behavior
        :type parent: tk.Widget | None
        :param title: Window title
        :type title: str
        :param message: Message text displayed in the dialog
        :type message: str
        :param theme: Theme configuration dictionary (bg/fg colors)
        :type theme: dict
        :param buttons: Tuple of (label, return_value) button definitions
        :type buttons: tuple
        :return: The value associated with the clicked button, or None
        :rtype: bool | None
        """

        # Extract theme colors
        bg: str = theme["bg"]
        fg: str = theme["fg"]

        # Result returned by the dialog
        result: bool | None = None

        # Create top-level modal window
        win = tk.Toplevel(parent)
        win.title(title)
        win.geometry(f"{WIDTH}x{HEIGHT}")
        win.configure(bg=bg)
        set_window_icon(win)
        win.resizable(False, False)
        win.transient(parent)
        win.grab_set()

        # Center window relative to parent
        center_window(win, parent)

        # Main container
        container = ttk.Frame(win, padding=20)
        container.pack(fill="both", expand=True)

        # Configure styles
        style = ttk.Style(win)
        style.configure("Msg.TFrame", background=bg)
        style.configure("Msg.TLabel", background=bg, foreground=fg, wraplength=400)
        style.configure("Msg.TButton", padding=6)

        container.configure(style="Msg.TFrame")

        # Message label
        ttk.Label(
            container,
            text=message,
            style="Msg.TLabel",
            justify="center"
        ).pack(expand=True, pady=(10, 20))

        # Button container
        btn_frame = ttk.Frame(container, style="Msg.TFrame")
        btn_frame.pack(fill="x")

        def on_click(result_value: Any) -> None:
            """
            Handle button click and close the dialog.

            :param result_value: Value associated with the clicked button
            :type result_value: Any
            """

            nonlocal result
            result = result_value
            win.destroy()

        total_buttons: int = len(buttons)


        if total_buttons == 1:
            # Single centered button
            text, value = buttons[0]

            btn_frame.columnconfigure(0, weight=1)

            ttk.Button(
                btn_frame,
                text=text,
                width=BTN_WIDTH,
                style="Msg.TButton",
                command=partial(on_click, value)
            ).grid(row=0, column=0, pady=5)

        else:
            # Multiple buttons with equal spacing
            btn_frame.columnconfigure(tuple(range(total_buttons)), weight=1)

            for col, (text, value) in enumerate(buttons):
                ttk.Button(
                    btn_frame,
                    text=text,
                    width=BTN_WIDTH,
                    style="Msg.TButton",
                    command=partial(on_click, value)
                ).grid(
                    row=0,
                    column=col,
                    padx=10,
                    pady=5
                )

        win.wait_window()

        return result

    # ======================
    # PUBLIC METHODS
    # ======================
    @staticmethod
    def ask_yes_no(*, parent=None, title: str = "", message: str = "", theme: dict | None = None) -> bool:
        """
        Display a Yes/No confirmation dialog.

        :param parent: Parent window
        :type parent: tk.Widget | None
        :param title: Dialog title
        :type title: str
        :param message: Dialog message
        :type message: str
        :param theme: Theme configuration dictionary
        :type theme: dict | None
        :return: True if Yes was selected, False otherwise
        :rtype: bool
        """

        return ThemedMessageBox._base_dialog(
            parent=parent,
            title=title,
            message=message,
            theme=theme,
            buttons=(
                (i18n.t("yes"), True),
                (i18n.t("no"), False),
            )
        )

    @staticmethod
    def show_error(*, parent=None, title: str = "", message: str = "", theme: dict | None = None) -> dict | None:
        """
        Display an error message dialog.

        :param parent: Parent window
        :type parent: tk.Widget | None
        :param title: Dialog title
        :type title: str
        :param message: Error message
        :type message: str
        :param theme: Theme configuration dictionary
        :type theme: dict | None
        """

        ThemedMessageBox._base_dialog(
            parent=parent,
            title=title,
            message=message,
            theme=theme,
            buttons=(("OK", None),)
        )

    @staticmethod
    def show_warning(*, parent=None, title: str = "", message: str = "", theme: dict | None = None) -> dict | None:
        """
        Display a warning message dialog.

        :param parent: Parent window
        :type parent: tk.Widget | None
        :param title: Dialog title
        :type title: str
        :param message: Warning message
        :type message: str
        :param theme: Theme configuration dictionary
        :type theme: dict | None
        """

        ThemedMessageBox._base_dialog(
            parent=parent,
            title=title,
            message=message,
            theme=theme,
            buttons=(("OK", None),)
        )

    @staticmethod
    def info(*, parent: tk.Widget | None=None, title: str, message: str, theme: dict | None=None) -> dict | None:
        """
        Display an informational message dialog.

        :param parent: Parent window
        :type parent: tk.Widget | None
        :param title: Dialog title
        :type title: str
        :param message: Information message
        :type message: str
        :param theme: Theme configuration dictionary
        :type theme: dict | None
        """

        ThemedMessageBox._base_dialog(
            parent=parent,
            title=title,
            message=message,
            theme=theme,
            buttons=(("OK", None),)
        )
