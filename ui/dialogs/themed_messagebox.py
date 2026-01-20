# ui/dialogs/themed_messagebox.py

import tkinter as tk

from tkinter import ttk
from functools import partial

from utils.app_config import load_config
from i18n.manager import I18nManager
from utils.window import center_window, set_window_icon



WIDTH = 460
HEIGHT = 220
BTN_WIDTH = 12

config: dict = load_config()
language: str = config.get("language", "en-US")
i18n: I18nManager = I18nManager(language=language)


class ThemedMessageBox:

    @staticmethod
    def _base_dialog(
        *,
        parent=None,
        title: str,
        message: str,
        theme: dict,
        buttons: tuple
    ) -> bool | None:

        bg = theme["bg"]
        fg = theme["fg"]

        result = None

        win = tk.Toplevel(parent)
        win.title(title)
        win.geometry(f"{WIDTH}x{HEIGHT}")
        win.configure(bg=bg)
        set_window_icon(win)
        win.resizable(False, False)
        win.transient(parent)
        win.grab_set()

        center_window(win, parent)

        container = ttk.Frame(win, padding=20)
        container.pack(fill="both", expand=True)

        style = ttk.Style(win)
        style.configure("Msg.TFrame", background=bg)
        style.configure("Msg.TLabel", background=bg, foreground=fg, wraplength=400)
        style.configure("Msg.TButton", padding=6)

        container.configure(style="Msg.TFrame")

        ttk.Label(
            container,
            text=message,
            style="Msg.TLabel",
            justify="center"
        ).pack(expand=True, pady=(10, 20))

        btn_frame = ttk.Frame(container, style="Msg.TFrame")
        btn_frame.pack(fill="x")

        def on_click(result_value):
            nonlocal result
            result = result_value
            win.destroy()

        total_buttons = len(buttons)


        if total_buttons == 1:
            # 🔹 Botão único centralizado
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
            # 🔹 Múltiplos botões com tamanho controlado
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
    def ask_yes_no(*, parent=None, title="", message="", theme=None) -> bool:
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
    def show_error(*, parent=None, title="", message="", theme=None):
        ThemedMessageBox._base_dialog(
            parent=parent,
            title=title,
            message=message,
            theme=theme,
            buttons=(("OK", None),)
        )

    @staticmethod
    def show_warning(*, parent=None, title="", message="", theme=None):
        ThemedMessageBox._base_dialog(
            parent=parent,
            title=title,
            message=message,
            theme=theme,
            buttons=(("OK", None),)
        )

    @staticmethod
    def info(*, parent=None, title: str, message: str, theme=None) -> None:
        ThemedMessageBox._base_dialog(
            parent=parent,
            title=title,
            message=message,
            theme=theme,
            buttons=(("OK", None),)
        )
