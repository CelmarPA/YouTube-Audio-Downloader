# ui/main_window.py

import os
import sys
import re
import tkinter as tk
from threading import Thread
from tkinter import ttk, messagebox

from widgets import download_dir, choose_folder, open_download_folder
from utils import resource_path
from core import Downloader


class AppWindow:
    def __init__(self):
        self.root = tk.Tk()

        # factory
        self.download = Downloader

        # estado
        self._init_state()
        self._generate_window()
        self._build_ui()

        self.is_paused = False

        self.root.mainloop()



    # =========================
    # Estado inicial
    # =========================
    def _init_state(self):
        self.download_dir = download_dir
        self.format_var = tk.StringVar(value="mp3")
        self.quality_var = tk.StringVar(value="192")
        self.playlist_var = tk.BooleanVar()
        self.keep_original_var = tk.BooleanVar()
        self.normalize_var = tk.BooleanVar()
        self.folder_var = tk.StringVar(value=self.download_dir)
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Aguardando")

    # =========================
    # Janela
    # =========================
    def _generate_window(self):
        self.root.title("YouTube Audio Downloader")
        self.root.geometry("620x480")
        self.root.resizable(False, False)

        self.root._icon_img = None

        icon_ico = resource_path("assets/icon.ico")
        icon_png = resource_path("assets/icon.png")

        if sys.platform.startswith("win"):
            try:
                self.root.iconbitmap(icon_ico)
                return
            except Exception:
                pass

        try:
            self.root._icon_img = tk.PhotoImage(file=icon_png)
            self.root.iconphoto(True, self.root._icon_img)
        except Exception:
            pass

    # =========================
    # UI
    # =========================
    def _build_ui(self):
        self._build_url()
        self._build_options()
        self._build_folder()
        self._build_progress()
        self._build_actions()
        self._build_log()



    def _build_url(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame, text="URL do YouTube:").grid(row=0, column=0, sticky="w")
        self.url_entry = ttk.Entry(frame)
        self.url_entry.grid(row=0, column=1, padx=8, sticky="ew")

        frame.columnconfigure(1, weight=1)

    def _build_options(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame, text="Formato").grid(row=0, column=0)
        ttk.Combobox(
            frame,
            textvariable=self.format_var,
            values=["mp3", "wav", "flac"],
            width=7,
            state="readonly"
        ).grid(row=0, column=1)

        ttk.Label(frame, text="Qualidade").grid(row=0, column=2, padx=5)
        ttk.Combobox(
            frame,
            textvariable=self.quality_var,
            values=["128", "192", "320"],
            width=7,
            state="readonly"
        ).grid(row=0, column=3)

        ttk.Checkbutton(frame, text="Baixar playlist", variable=self.playlist_var).grid(row=0, column=4, padx=5)
        ttk.Checkbutton(frame, text="Manter original", variable=self.keep_original_var).grid(row=0, column=5, padx=5)
        ttk.Checkbutton(frame, text="Normalizar áudio", variable=self.normalize_var).grid(row=0, column=6, padx=5)

    def _build_folder(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame, text="Salvar em:").grid(row=0, column=0)
        ttk.Entry(frame, textvariable=self.folder_var, state="readonly").grid(row=0, column=1, padx=8, sticky="ew")

        ttk.Button(frame, text="Escolher...", command=self.on_choose_folder).grid(row=0, column=2)

        frame.columnconfigure(1, weight=1)

    def _build_progress(self):
        ttk.Progressbar(
            self.root,
            variable=self.progress_var,
            maximum=100
        ).pack(fill="x", padx=10, pady=5)

        ttk.Label(self.root, textvariable=self.status_var).pack(anchor="w", padx=10)

    def _build_actions(self):
        self.download_button = ttk.Button(self.root, text="Baixar", command=self.start_download)
        self.download_button.pack(pady=8)

        # Pausar / Retomar (botão único)
        self.pause_resume_button = ttk.Button(self.root, text="Pausar", command=self.on_pause_resume_clicked, state="disabled")
        self.pause_resume_button.pack(pady=4)

        self.cancel_button = ttk.Button(self.root, text="Cancelar", command=self.on_cancel_clicked, state="disabled")
        self.cancel_button.pack(pady=4)

        ttk.Button(self.root, text="Abrir pasta", command=self.on_open_folder).pack(pady=4)

    def _build_log(self):
        ttk.Label(self.root, text="Log").pack(anchor="w", padx=10)

        self.log_text = tk.Text(self.root, height=8, state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=10, pady=5)

    def on_choose_folder(self):
        folder = choose_folder()
        if folder:
            self.folder_var.set(folder)

    def on_open_folder(self):
        open_download_folder(self.folder_var.get())

    # =========================
    # Download
    # =========================
    def start_download(self):
        url = self.url_entry.get().strip()

        if not url:
            messagebox.showerror("Erro", "Informe a URL do YouTube")
            return

        if not re.match(r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+', url):
            messagebox.showerror("Erro", "Informe uma URL válida do YouTube")
            return

        self.download_button.config(state="disabled")
        self.pause_resume_button.config(state="normal", text="Pausar")
        self.cancel_button.config(state="normal")
        self.is_paused = False

        self.progress_var.set(0)
        self.status_var.set("Iniciando...")
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state="disabled")

        Thread(target=self.run_download, daemon=True).start()

    def run_download(self):
        try:
            os.makedirs(self.folder_var.get(), exist_ok=True)

            self.downloader = self.download(
                url=self.url_entry.get().strip(),
                output_path=self.folder_var.get(),
                audio_format=self.format_var.get(),
                quality=self.quality_var.get(),
                allow_playlist=self.playlist_var.get(),
                keep_original_file=self.keep_original_var.get(),
                normalize_enabled=self.normalize_var.get(),
                progress_hook=self.on_progress,
                status_hook=self.set_status,
                file_finished_hook=self.on_file_finished,
                error_hook=self.on_error,
                log_hook=self._log
            )

            self.downloader.start()

        finally:
            self.root.after(
                0,
                lambda: (
                    self.download_button.config(state="normal"),
                    self.cancel_button.config(
                        text="Cancelar",
                        state="disabled"
                    ),
                    self.pause_resume_button.config(
                        state="disabled",
                        text="Pausar"
                    ),
                    setattr(self, "is_paused", False),
                    self.status_var.set("Aguardando")
                )
            )

    # =========================
    # Hooks (THREAD-SAFE)
    # =========================
    def on_progress(self, percent, item_index=None, total_items=None):
        """
        Atualiza barra de progresso e status.
        - percent: 0 a 100
        - item_index: índice atual da playlist (opcional)
        - total_items: total de itens na playlist (opcional)
        """

        percent = min(max(percent, 0), 100)     # garante entre 0 e 100

        def update():
            self.progress_var.set(percent)
            status_text = f"Progresso: {percent:.1f}%"

            if item_index and total_items:
                status_text = f"Item {item_index}/{total_items} — {status_text}"

            self.status_var.set(status_text)

        self.root.after(0, update)

    def set_status(self, text):
        self.root.after(0, lambda: self.status_var.set(text))

    def on_file_finished(self, filename):
        def update():
            self._log(f"Finalizado: {os.path.basename(filename)}")
            self.progress_var.set(0)

        self.root.after(0, update)

    def on_error(self, message):
        self.root.after(0, lambda: messagebox.showerror("Erro", message))

    # =========================
    # Log
    # =========================
    def _log(self, text):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def on_pause_resume_clicked(self):
        if not self.is_paused:
            # PAUSAR
            self.downloader.pause()
            self.is_paused = True
            self.pause_resume_button.config(text="Retomar")

        else:
            # RETOMAR
            self.downloader.resume()
            self.is_paused = False
            self.pause_resume_button.config(text="Pausar")

    def on_cancel_clicked(self):
        if not hasattr(self, "downloader") or not self.downloader:
            return

        # PLAYLIST
        if self.downloader.allow_playlist:
            if not messagebox.askyesno(
                    "Cancelar playlist",
                    "Deseja cancelar após o item atual terminar?"
            ):
                return

            self.status_var.set("⏭️ Finalizando item atual da playlist...")
            self._log("⏭️ Cancelamento solicitado (aguardando item atual terminar)")

        # VÍDEO ÚNICO
        else:
            self.status_var.set("Cancelando download...")
            self._log("❌ Cancelamento solicitado: download será interrompido imediatamente.")

        self.cancel_button.config(state="disabled")
        self.downloader.cancel()

    def on_download_finished(self):
        self.cancel_button.config(
            text="Cancelar",
            state="disabled"
        )
