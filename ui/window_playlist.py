import tkinter as tk
from tkinter import ttk

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
            var = tk.BooleanVar(value=True)

            title = entry.get("title", "untitled")
            duration = entry.get("duration", "0")

            # Usa função para formatar duração para mm:ss ou hh:mm:ss
            duration_str = duration_format(duration_sec=duration)

            chk = tk.Checkbutton(
                self.inner_frame,
                text=f"{i}. {title} [{duration_str}]",
                variable=var,
                anchor="w",
                justify="left",
                wraplength=500
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
