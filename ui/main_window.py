# ui/main_window.py

import tkinter as tk
import sys
from threading import Thread

from tkinter import ttk, messagebox
from widgets import download_dir, choose_folder, open_download_folder
from utils import resource_path


class AppWindow:

    def __init__(self):
        self.root = tk.Tk()

        # declaração explícita dos atributos de instância
        self.download_dir = None
        self.format_var = None
        self.quality_var = None
        self.playlist_var = None
        self.folder_var = None
        self.progress_var = None
        self.status_var = None

        self.url_frame = None
        self.url_label = None
        self.url_entry = None

        self.opts_frame = None
        self.opts_format_label = None
        self.format_combo = None
        self.opts_quality_label = None
        self.quality_combo = None
        self.playlist_check_button = None

        self.folder_frame = None
        self.folder_label = None
        self.folder_entry = None
        self.choose_folder_button = None

        self.progress = None
        self.status_label = None

        self.download_button = None
        self.open_folder_button = None

        self.log_label = None
        self.log_text = None

        self.init_state()

        self.generate_window()

        self.choose_folder = choose_folder
        self.open_download_folder = open_download_folder

        self.build_ui()

        self.bind_events()

        self.root.mainloop()

    def init_state(self):
        self.download_dir = download_dir
        self.format_var = tk.StringVar(value="mp3")
        self.quality_var = tk.StringVar(value="192")
        self.playlist_var = tk.BooleanVar()
        self.folder_var = tk.StringVar(value=self.download_dir)
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Aguardando")

    def generate_window(self):
        self.root.title("YouTube Audio Downloader")
        self.root.geometry("620x480")
        self.root.resizable(False, False)

        self.root._icon_img = None  # evita garbage collection

        icon_ico = resource_path("assets/icon.ico")
        icon_png = resource_path("assets/icon.png")

        if sys.platform.startswith("win"):
            try:
                self.root.iconbitmap(icon_ico)

                return

            except Exception as e:
                print(f"Falha ao carregar .ico: {e}")

        # Fallback universal (Linux / macOS / erro no Windows)
        try:
            self.root._icon_img = tk.PhotoImage(file=icon_png)
            self.root.iconphoto(True, self.root._icon_img)

        except Exception as e:
            print(f"Falha ao carregar .png: {e}")

    def create_url_widgets(self):
        self.url_frame = ttk.Frame(self.root)

        self.url_label = ttk.Label(self.url_frame, text="URL do YouTube:")

        self.url_entry = ttk.Entry(self.url_frame)

    def layout_url_widgets(self):
        self.url_frame.pack(fill="x", padx=10, pady=10)

        self.url_label.grid(row=0, column=0, sticky="w")
        self.url_entry.grid(row=0, column=1, padx=8, sticky="ew")

        self.url_frame.columnconfigure(1, weight=1)

    def create_options_widgets(self):
        self.opts_frame = ttk.Frame(self.root)

        self.opts_format_label = ttk.Label(self.opts_frame, text="Formato")

        self.format_combo = ttk.Combobox(
            self.opts_frame,
            textvariable=self.format_var,
            values=["mp3", "wav", "flac"],
            width=7,
            state="readonly"
        )

        self.opts_quality_label = ttk.Label(self.opts_frame, text="Qualidade")

        self.quality_combo = ttk.Combobox(
            self.opts_frame,
            textvariable=self.quality_var,
            values=["128", "192", "320"],
            width=7,
            state="readonly"
        )

        self.playlist_check_button = ttk.Checkbutton(
            self.opts_frame,
            text="Baixar playlist",
            variable=self.playlist_var,
        )

    def layout_options_widgets(self):
        self.opts_frame.pack(fill="x", padx=10, pady=10)

        self.opts_frame.columnconfigure(5, weight=1)

        self.opts_format_label.grid(row=0, column=0, padx=5)

        self.format_combo.grid(row=0, column=1)

        self.opts_quality_label.grid(row=0, column=2, padx=5)

        self.quality_combo.grid(row=0, column=3)

        self.playlist_check_button.grid(row=0, column=4, padx=10)

    def create_folder_widgets(self):
        self.folder_frame = ttk.Frame(self.root)

        self.folder_label = ttk.Label(self.folder_frame, text="Salvar em:")

        self.folder_entry = ttk.Entry(self.folder_frame, textvariable=self.folder_var, state="readonly")

        self.choose_folder_button = ttk.Button(self.folder_frame, text="Escolher...", width=12)

    def layout_folder_widgets(self):
        self.folder_frame.pack(fill="x", padx=10, pady=5)

        self.folder_frame.columnconfigure(0, weight=0)
        self.folder_frame.columnconfigure(1, weight=1)
        self.folder_frame.columnconfigure(2, weight=0)

        self.folder_label.grid(row=0, column=0, sticky="w")

        self.folder_entry.grid(row=0, column=1, padx=8, sticky="ew")

        self.choose_folder_button.grid(row=0, column=2)

    def create_progress_widgets(self):
        self.progress = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100)

        self.status_label = ttk.Label(self.root, textvariable=self.status_var)

    def layout_progress_widgets(self):
        self.progress.pack(fill="x", padx=10, pady=5)

        self.status_label.pack(anchor="w", padx=10)

    def create_action_widgets(self):
        self.download_button = ttk.Button(self.root, text="Baixar")

        self.open_folder_button = ttk.Button(self.root, text="Abrir pasta")

    def layout_action_widgets(self):
        self.download_button.pack(pady=8)

        self.open_folder_button.pack()

    def create_log_widgets(self):
        self.log_label = ttk.Label(self.root, text="Log")

        self.log_text = tk.Text(self.root, height=8, state="disabled")

    def layout_log_widgets(self):
        self.log_label.pack(anchor="w", padx=10)

        self.log_text.pack(fill="both", expand=True, padx=10, pady=5)

    def build_ui(self):
        self.create_url_widgets()
        self.layout_url_widgets()

        self.create_options_widgets()
        self.layout_options_widgets()

        self.create_folder_widgets()
        self.layout_folder_widgets()

        self.create_progress_widgets()
        self.layout_progress_widgets()

        self.create_action_widgets()
        self.layout_action_widgets()

        self.create_log_widgets()
        self.layout_log_widgets()

    def log(self, text):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def on_choose_folder(self):
        folder = choose_folder()

        if folder:
            self.folder_var.set(folder)

    def on_open_folder(self):
        path = self.folder_var.get()

        if path:
            open_download_folder(path)

    def bind_events(self):
        self.choose_folder_button.config(command=self.choose_folder)
        self.download_button.config(command=self.start_download)
        self.open_folder_button.config(command=self.on_choose_folder)

    def start_download(self):
        url = self.url_entry.get().strip()

        if not url:
            messagebox.showerror("Erro", "Informe a URL do YouTube")

            return

        self.download_button.config(state="disabled")
        self.progress_var.set(0)
        self.status_var.set("Iniciando...")
        self.log_text.delete("1.0", tk.END)

        Thread(target=self.run_download, daemon=True).start()

    def run_download(self):
        print("Ok")
        pass
