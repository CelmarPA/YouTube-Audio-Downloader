# utils/window.py

import tkinter as tk
from utils.paths import resource_path


def set_window_icon(win: tk.Tk | tk.Toplevel) -> None:
    try:
        icon_path = resource_path("assets/icon.ico")
        win.iconbitmap(icon_path)
    except Exception as e:
        _e = e
        # fallback para PNG se necessário

        try:
            icon = tk.PhotoImage(file=resource_path("assets/icon.png"))
            win.iconphoto(True, icon)
            win._icon_ref = icon  # evita GC

        except Exception as e:
            _e = e
            pass


def center_window(win, parent=None):
    win.update_idletasks()

    width = win.winfo_width()
    height = win.winfo_height()

    if parent:
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()

        x = px + (pw // 2) - (width // 2)
        y = py + (ph // 2) - (height // 2)
    else:
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()

        x = (sw // 2) - (width // 2)
        y = (sh // 2) - (height // 2)

    win.geometry(f"{width}x{height}+{x}+{y}")
