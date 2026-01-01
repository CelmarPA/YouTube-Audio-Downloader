import tkinter as tk
from tkinter import ttk
import os
from utils import is_normalized

def duration_format(duration_sec):
    if duration_sec >= 3600:
        hours = duration_sec // 3600
        minutes = (duration_sec % 3600) // 60
        seconds = duration_sec % 60

        duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"

    else:
        minutes = duration_sec // 60
        seconds = duration_sec % 60

        duration_str = f"{minutes}:{seconds:02d}"

    return duration_str


def mark_already_downloaded(
    entries,
    playlist_dir,
    audio_format,
    keep_original,
    normalize_audio
):
    """
    Marca entradas da playlist como já baixadas, levando em conta:
    - existência de áudio
    - existência de vídeo (se keep_original)
    - normalização real por LUFS (se normalize_audio)
    """

    if not os.path.isdir(playlist_dir):
        return

    audio_ext = f".{audio_format.lower()}"

    for entry in entries:
        entry["_already_downloaded"] = False

        video_id = entry.get("id")
        if not video_id:
            continue

        audio_found = False
        video_found = False
        audio_path = None

        # 🔍 Procura arquivos do vídeo na pasta da playlist
        for root, _, files in os.walk(playlist_dir):
            for file in files:
                if f"[{video_id}]" not in file:
                    continue

                lower = file.lower()

                if lower.endswith(audio_ext):
                    audio_found = True
                    audio_path = os.path.join(root, file)

                elif lower.endswith(".mp4"):
                    video_found = True

            # ✅ só sai quando tudo necessário foi encontrado
            if audio_found and (not keep_original or video_found):
                break

        # =========================
        # 🔒 REGRA FINAL ÚNICA
        # =========================
        already = False

        if normalize_audio:
            # precisa existir áudio E estar normalizado
            if audio_found and audio_path and is_normalized(audio_path):
                if keep_original:
                    already = video_found
                else:
                    already = True
        else:
            # normalização desligada
            if keep_original:
                already = audio_found and video_found
            else:
                already = audio_found

        entry["_already_downloaded"] = already


class PlaylistFrame(tk.Toplevel):

    def __init__(self, master, playlist_title, entries):
        super().__init__(master)
        self.title("Selecionar vídeos da playlist")
        self.geometry("550x400")
        self.entries = list(entries)
        self.check_vars = []
        self.selected = None    # Lista de entradas selecionadas ou None se cancelado

        # Mostrar o nome da playlist no topo
        self.playlist_label = ttk.Label(self, text=f"Playlist: {playlist_title}", font=("TkDefaultFont", 12, "bold"))
        self.playlist_label.pack(anchor="w", padx=10, pady=5)

        # Frame principal com canvas + scrollbar
        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(self.canvas_frame)
        self.scrollbar = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.inner_frame = tk.Frame(self.canvas)

        self.inner_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self._populate()

        # Rodapé com botões
        self.footer_frame = ttk.Frame(self)
        self.footer_frame.pack(fill="x", padx=10, pady=(5, 10))  # Espaçamento do rodapé

        self._build_buttons()

        # Modal: bloqueia a janela principal
        self.grab_set()
        self.focus_set()
        self.transient(master)

    def _populate(self):
        for i, entry in enumerate(self.entries, start=1):
            already = entry.get("_already_downloaded", False)
            print(f"VERIFICANDOOOOOOO: {already}")
            title = entry.get("title", "Playlist")
            # 🔥 CORREÇÃO AQUI
            var = tk.BooleanVar(
                value=entry.get("__preselected__", False)
            )

            title = entry.get("title", "untitled")
            duration = entry.get("duration", 0)

            duration_str = duration_format(duration_sec=duration)
            text = f"{i}. {title} [{duration_str}]"

            if already:
                text = f"✔ {text} (já baixado)"

            chk = tk.Checkbutton(
                self.inner_frame,
                text=text,
                variable=var,
                anchor="w",
                justify="left",
                wraplength=500,
                fg="gray" if already else "black",
                state="disabled" if already else "normal"
            )
            chk.pack(fill="x", anchor="w", pady=2)

            self.check_vars.append(var)

    def _build_buttons(self):
        # Frame dos botões (alinhado à esquerda)
        frame = ttk.Frame(self.footer_frame)
        frame.pack(anchor="w", pady=(5, 0))  # Alinhado à esquerda, um pouco abaixo

        ttk.Button(frame, text="Selecionar Todos", command=self.select_all).pack(side="left", padx=(0, 5))
        ttk.Button(frame, text="Desmarcar Todos", command=self.deselect_all).pack(side="left", padx=(0, 20))

        ttk.Button(frame, text="Baixar", command=self.on_ok).pack(side="left")
        ttk.Button(frame, text="Cancelar", command=self.on_cancel).pack(side="left", padx=(0, 5))

    def select_all(self):
        for var in self.check_vars:
            var.set(True)

    def deselect_all(self):
        for var in self.check_vars:
            var.set(False)

    def on_ok(self):
        self.selected = self.get_selected_entries()
        self.destroy()

    def on_cancel(self):
        self.selected = None
        self.destroy()

    def get_selected_entries(self):
        selected = []

        for var, entry in zip(self.check_vars, self.entries):
            if var.get():
                selected.append(entry)

        return selected
