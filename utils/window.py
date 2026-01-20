# utils/window.py

import tkinter as tk
from utils.paths import resource_path


def set_window_icon(win: tk.Tk | tk.Toplevel) -> None:
    """
    Set the application window icon.

    Tries to load an ICO icon first. If it fails, falls back to a PNG icon.
    Keeps a reference to the PNG icon to avoid garbage collection.

    :param win: Target window instance
    :type win: tk.Tk | tk.Toplevel
    :return: None
    :rtype: None
    """
    try:
        icon_path: str = resource_path("assets/icon.ico")
        win.iconbitmap(icon_path)

    except Exception as e:
        _e = e

        try:
            icon: tk.PhotoImage = tk.PhotoImage(file=resource_path("assets/icon.png"))
            win.iconphoto(True, icon)
            win._icon_ref = icon  # evita GC

        except Exception as e:
            _e = e
            pass


def center_window(win: tk.Tk | tk.Toplevel, parent: tk.Tk | tk.Toplevel=None):
    """
    Center a window on the screen or relative to a parent window.

    If a parent window is provided, the window is centered relative
    to the parent. Otherwise, it is centered on the screen.

    :param win: Window to be centered
    :type win: tk.Tk | tk.Toplevel
    :param parent: Optional parent window
    :type parent: tk.Tk | tk.Toplevel | None
    :return: None
    :rtype: None
    """

    win.update_idletasks()

    width: int = win.winfo_width()
    height: int = win.winfo_height()

    if parent:
        px: int = parent.winfo_rootx()
        py: int = parent.winfo_rooty()
        pw: int = parent.winfo_width()
        ph: int = parent.winfo_height()

        x: int = px + (pw // 2) - (width // 2)
        y: int = py + (ph // 2) - (height // 2)
    else:
        sw: int = win.winfo_screenwidth()
        sh: int = win.winfo_screenheight()

        x: int = (sw // 2) - (width // 2)
        y: int = (sh // 2) - (height // 2)

    win.geometry(f"{width}x{height}+{x}+{y}")
