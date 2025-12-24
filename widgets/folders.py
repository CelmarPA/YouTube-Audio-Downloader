import os.path
import subprocess
import sys
from pathlib import Path
from tkinter import filedialog, messagebox


def get_default_downloads():
    return str(Path.home() / "Downloads")


download_dir = get_default_downloads()


def choose_folder():
    global download_dir

    folder = filedialog.askdirectory()

    if folder:
        download_dir = folder

    return download_dir


def open_download_folder(path):
    path = os.path.abspath(path)

    try:
        if sys.platform.startswith("win"):
            os.startfile(path)

            return

        elif "microsoft" in os.uname().release.lower():
            result = subprocess.run(
                ["wslpath", '-w', path],
                capture_output=True,
                text=True
            )

            win_path = result.stdout.strip()

            subprocess.Popen(["explorer.exe", win_path])

            return

        elif sys.platform.startswith("darwin"):
            subprocess.call(["open", path])

            return

        subprocess.call(["xdg-open", path])

    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível abrir a pasta:\n{e}")
        print(f"Não foi possível abrir a pasta:\n{e}")




