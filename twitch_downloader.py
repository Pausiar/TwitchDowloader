import os
import re
import sys
import threading
import webbrowser
from pathlib import Path

import tkinter as tk
from tkinter import filedialog

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

APP_NAME = "Twitch VOD Downloader"
APP_VERSION = "1.1.0"
SITE = "https://pausiar.github.io/TwitchDowloader/"
GUIDE_URL = SITE + "guia-descarga-responsable.html"
TERMS_URL = SITE + "terminos.html"

PAPER = "#F7F9FC"
PANEL = "#EEF2F8"
INK = "#1A1F2B"
INK_2 = "#414B5C"
MUTED = "#5F6B7E"
RULE = "#DDE3EC"
RULE_2 = "#C9D2E0"
ACCENT = "#2E62E8"
ACCENT_DEEP = "#1E45A8"
ACCENT_WASH = "#EAF0FE"
GRAPHITE = "#171C26"
GRAPHITE_INK = "#E9EEF7"
ERROR = "#B3261E"
SUCCESS = "#1C6B45"

FONT = "Segoe UI"
FONT_DISPLAY = "Segoe UI Semibold"
FONT_MONO = "Consolas"

TITLE = 21
LEAD = 10
BODY = 10
SMALL = 9


def resource_path(*parts):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *parts)


def format_bytes(value):
    if not value:
        return "0 MB"
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(value)
    index = 0
    while size >= 1000 and index < len(units) - 1:
        size /= 1000
        index += 1
    if index <= 1:
        return f"{size:.0f} {units[index]}"
    return f"{size:.1f} {units[index]}".replace(".", ",")


def format_eta(seconds):
    if seconds is None or seconds < 0:
        return None
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds} s"
    minutes, rest = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes} min"
    hours, minutes = divmod(minutes, 60)
    return f"{hours} h {minutes:02d} min"


class FlatButton(tk.Button):
    def __init__(self, master, tone="quiet", **kwargs):
        palette = {
            "primary": (ACCENT, "#FFFFFF", ACCENT_DEEP, RULE_2, "#FFFFFF"),
            "quiet": ("#FFFFFF", INK, PANEL, RULE_2, INK),
            "graphite": (GRAPHITE, GRAPHITE_INK, "#2A3140", GRAPHITE, GRAPHITE_INK),
            "link": (None, INK_2, None, None, None),
        }[tone]
        bg, fg, active_bg, ring, ring_focus = palette
        super().__init__(
            master,
            bg=bg or PAPER,
            fg=fg,
            activebackground=active_bg or PANEL,
            activeforeground=fg,
            disabledforeground=MUTED,
            relief="flat",
            bd=0,
            cursor="hand2",
            highlightthickness=2 if ring else 0,
            highlightbackground=ring or PAPER,
            highlightcolor=ring_focus or ACCENT,
            takefocus=True,
            **kwargs,
        )
        self._tone = tone
        if tone == "link":
            self.configure(bg=PAPER, cursor="hand2")
            self.bind("<Enter>", lambda _e: self.configure(fg=ACCENT))
            self.bind("<Leave>", lambda _e: self.configure(fg=INK_2))


class ProgressBar(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, height=10, bg=PANEL, highlightthickness=0, bd=0, **kwargs)
        self._value = 0.0
        self.bind("<Configure>", lambda _e: self._draw())

    def set(self, value):
        self._value = max(0.0, min(1.0, value))
        self._draw()

    def _draw(self):
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        self.create_rectangle(0, 0, width, height, fill=RULE_2, outline="")
        if self._value > 0:
            self.create_rectangle(0, 0, int(width * self._value), height, fill=ACCENT, outline="")


class TwitchDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("820x660")
        self.root.minsize(760, 620)
        self.root.configure(bg=PAPER)

        try:
            self.root.iconbitmap(resource_path("assets", "logo.ico"))
        except Exception:
            pass

        self.url_var = tk.StringVar()
        self.output_dir = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.status_text = tk.StringVar(value="Listo para descargar")
        self.detail_text = tk.StringVar(value="Pega un enlace de Twitch para empezar.")
        self.location_text = tk.StringVar(value="")
        self.is_downloading = False
        self.cancelled = False
        self.last_file = None

        self._build()
        if yt_dlp is None:
            self.status_text.set("Falta yt-dlp")
            self.detail_text.set("Usa el .exe de la release o instala requirements.txt.")

    def _build(self):
        self._build_header()

        body = tk.Frame(self.root, bg=PAPER)
        body.pack(fill="both", expand=True, padx=28, pady=(22, 0))

        tk.Label(body, text="Descarga el VOD. Guarda el archivo.", font=(FONT_DISPLAY, TITLE),
                 bg=PAPER, fg=INK, anchor="w").pack(fill="x")
        tk.Label(
            body,
            text="Pega el enlace, elige la carpeta y descarga en la máxima calidad disponible.",
            font=(FONT, LEAD), bg=PAPER, fg=INK_2, anchor="w",
        ).pack(fill="x", pady=(6, 20))

        self._field(body, "Enlace del VOD o clip", self.url_var, paste=True)
        self._field(body, "Carpeta de destino", self.output_dir, browse=True)

        actions = tk.Frame(body, bg=PAPER)
        actions.pack(fill="x", pady=(6, 22))
        self.action_button = FlatButton(actions, tone="primary", text="Descargar",
                                        font=(FONT_DISPLAY, 10), padx=22, pady=10,
                                        command=self.toggle_download)
        self.action_button.pack(side="left")
        tk.Label(actions, text="Windows 10 u 11, sin cuenta, sin instalar nada más",
                 font=(FONT, SMALL), bg=PAPER, fg=MUTED).pack(side="left", padx=14)

        self._build_status(body)
        self._build_footer()

        self.root.bind("<Return>", lambda _e: self.toggle_download())
        self.url_var.trace_add("write", self._on_url_change)

    def _build_header(self):
        header = tk.Frame(self.root, bg=PAPER, height=64)
        header.pack(fill="x", padx=28, pady=(16, 0))
        header.pack_propagate(False)

        mark = tk.Canvas(header, width=26, height=26, bg=PAPER, highlightthickness=0)
        mark.pack(side="left", pady=18)
        mark.create_rectangle(2, 2, 24, 24, fill=ACCENT, outline="")
        mark.create_line(13, 7, 13, 16, fill=PAPER, width=2)
        mark.create_line(8, 12, 13, 17, 18, 12, fill=PAPER, width=2)
        mark.create_line(7, 20, 19, 20, fill=PAPER, width=2)

        tk.Label(header, text=APP_NAME, font=(FONT_DISPLAY, 11), bg=PAPER, fg=INK).pack(
            side="left", padx=(10, 0), pady=18
        )

        for label, url in (("Guía", GUIDE_URL), ("Términos", TERMS_URL)):
            FlatButton(header, tone="link", text=label, font=(FONT, SMALL),
                       command=lambda u=url: webbrowser.open(u)).pack(side="right", pady=18, padx=(14, 0))

        tk.Frame(self.root, bg=RULE, height=1).pack(fill="x", padx=28, pady=(10, 0))

    def _field(self, parent, label, variable, paste=False, browse=False):
        tk.Label(parent, text=label, font=(FONT, SMALL), bg=PAPER, fg=INK_2, anchor="w").pack(
            fill="x", pady=(0, 5)
        )
        row = tk.Frame(parent, bg=PAPER)
        row.pack(fill="x", pady=(0, 14))

        entry = tk.Entry(
            row, textvariable=variable, font=(FONT, BODY), bg="#FFFFFF", fg=INK,
            relief="flat", bd=0, highlightthickness=2, highlightbackground=RULE_2,
            highlightcolor=ACCENT, insertbackground=INK,
        )
        entry.pack(side="left", fill="x", expand=True, ipady=8)

        if paste:
            FlatButton(row, tone="quiet", text="Pegar", font=(FONT, SMALL), padx=14, pady=8,
                       command=lambda: self._paste_into(entry)).pack(side="left", padx=(8, 0))
        if browse:
            FlatButton(row, tone="quiet", text="Examinar", font=(FONT, SMALL), padx=14, pady=8,
                       command=self.browse_folder).pack(side="left", padx=(8, 0))
        return entry

    def _build_status(self, parent):
        panel = tk.Frame(parent, bg=PANEL, highlightthickness=1, highlightbackground=RULE)
        panel.pack(fill="both", expand=True, pady=(0, 20))

        inner = tk.Frame(panel, bg=PANEL)
        inner.pack(fill="both", expand=True, padx=18, pady=14)

        head = tk.Frame(inner, bg=PANEL)
        head.pack(fill="x")
        tk.Label(head, textvariable=self.status_text, font=(FONT_DISPLAY, 11),
                 bg=PANEL, fg=INK, anchor="w").pack(side="left")

        self.open_button = FlatButton(head, tone="quiet", text="Abrir carpeta",
                                      font=(FONT, SMALL), padx=12, pady=6,
                                      command=self.open_folder)

        self.progress = ProgressBar(inner)
        self.progress.pack(fill="x", pady=(12, 10))

        self.detail = tk.Label(inner, textvariable=self.detail_text, font=(FONT_MONO, SMALL),
                               bg=PANEL, fg=INK_2, anchor="w", justify="left")
        self.detail.pack(fill="x")

        self.location = tk.Label(inner, textvariable=self.location_text, font=(FONT_MONO, SMALL),
                                 bg=PANEL, fg=MUTED, anchor="w", justify="left")

    def _build_footer(self):
        tk.Frame(self.root, bg=RULE, height=1).pack(fill="x", padx=28)
        footer = tk.Frame(self.root, bg=PAPER)
        footer.pack(fill="x", padx=28, pady=12)
        tk.Label(
            footer,
            text="Uso personal. No afiliado ni respaldado por Twitch Interactive, Inc.",
            font=(FONT, SMALL), bg=PAPER, fg=MUTED,
        ).pack(side="left")
        tk.Label(footer, text=APP_VERSION, font=(FONT_MONO, SMALL), bg=PAPER, fg=MUTED).pack(side="right")

    def _paste_into(self, entry):
        try:
            text = self.root.clipboard_get()
        except Exception:
            text = ""
        if text:
            entry.delete(0, "end")
            entry.insert(0, text.strip())

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.output_dir.get() or None, mustexist=True)
        if folder:
            self.output_dir.set(os.path.normpath(folder))

    def validate_url(self, url):
        patterns = [
            r"https?://(www\.)?twitch\.tv/videos/\d+",
            r"https?://(www\.)?twitch\.tv/[^/\s]+/video/\d+",
            r"https?://(www\.)?twitch\.tv/[^/\s]+/clip/[^/\s]+",
            r"https?://clips\.twitch\.tv/[^/\s]+",
            r"https?://(www\.)?twitch\.tv/[^/\s]+/?$",
        ]
        return any(re.match(pattern, url) for pattern in patterns)

    def _on_url_change(self, *_args):
        if self.is_downloading:
            return
        url = self.url_var.get().strip()
        if not url:
            self.detail_text.set("Pega un enlace de Twitch para empezar.")
        elif self.validate_url(url):
            self.detail_text.set("Enlace válido. Elige la carpeta y pulsa Descargar.")
        else:
            self.detail_text.set("Ese enlace no parece un VOD o un clip de Twitch.")

    def toggle_download(self):
        if self.is_downloading:
            self.cancelled = True
            self.status_text.set("Cancelando")
            self.detail_text.set("Esperando a que yt-dlp cierre el archivo.")
            return
        self.start_download()

    def start_download(self):
        if yt_dlp is None:
            self.status_text.set("Falta yt-dlp")
            self.detail_text.set("Usa el .exe de la release o instala requirements.txt.")
            return

        url = self.url_var.get().strip()
        if not url:
            self.status_text.set("Falta el enlace")
            self.detail_text.set("Copia la URL del VOD o del clip y pégala en el campo de arriba.")
            return
        if not self.validate_url(url):
            self.status_text.set("Enlace no válido")
            self.detail_text.set("Formatos: twitch.tv/videos/123456789 o clips.twitch.tv/NombreDelClip")
            return

        folder = self.output_dir.get().strip()
        if not os.path.isdir(folder):
            self.status_text.set("Carpeta no encontrada")
            self.detail_text.set("Elige una carpeta existente con el botón Examinar.")
            return

        self.is_downloading = True
        self.cancelled = False
        self.last_file = None
        self.open_button.pack_forget()
        self.action_button.configure(text="Cancelar", bg=GRAPHITE, activebackground="#2A3140",
                                     fg=GRAPHITE_INK, activeforeground=GRAPHITE_INK)
        self.progress.set(0)
        self.status_text.set("Iniciando")
        self.detail_text.set("Conectando con Twitch.")
        self.location_text.set(f"Guardando en {folder}")
        if not self.location.winfo_manager():
            self.location.pack(fill="x", pady=(8, 0))

        thread = threading.Thread(target=self.download_video, args=(url, folder), daemon=True)
        thread.start()

    def download_video(self, url, folder):
        options = {
            "format": "best",
            "outtmpl": os.path.join(folder, "%(title)s.%(ext)s"),
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "progress_hooks": [self.progress_hook],
            "postprocessor_hooks": [self.postprocessor_hook],
        }
        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=True)
                if info:
                    self.last_file = ydl.prepare_filename(info)
            self.root.after(0, self.finish, True, "Descarga completada")
        except Exception as exc:
            cancelled = self.cancelled
            text = self._clean_error(exc)
            self.root.after(0, self.finish, False, "Descarga cancelada" if cancelled else text)

    def _clean_error(self, exc):
        text = str(exc).strip().splitlines()[0] if str(exc).strip() else exc.__class__.__name__
        text = re.sub(r"^ERROR:\s*", "", text)
        lowered = text.lower()
        for needle, message in (
            ("subscriber", "Solo para suscriptores"),
            ("unavailable", "VOD no disponible"),
            ("does not exist", "VOD no disponible"),
            ("404", "VOD no encontrado"),
            ("private", "VOD privado"),
            ("timed out", "No se pudo conectar"),
            ("connection", "No se pudo conectar"),
            ("login", "Inicia sesión en Twitch"),
        ):
            if needle in lowered:
                return message
        return text[:180]

    def progress_hook(self, data):
        if self.cancelled:
            raise yt_dlp.utils.DownloadCancelled("Cancelado por el usuario")
        status = data.get("status")
        if status == "downloading":
            total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
            done = data.get("downloaded_bytes") or 0
            ratio = (done / total) if total else 0
            speed = data.get("speed")
            eta = format_eta(data.get("eta"))
            parts = [f"{ratio * 100:.0f}%" if total else format_bytes(done)]
            if speed:
                parts.append(f"{format_bytes(speed)}/s")
            if eta:
                parts.append(f"faltan {eta}")
            self.root.after(0, self.update_progress, ratio, "Descargando", ", ".join(parts))
        elif status == "finished":
            self.root.after(0, self.update_progress, 1.0, "Procesando", "Comprobando el archivo descargado.")

    def postprocessor_hook(self, data):
        if data.get("status") == "started":
            name = data.get("postprocessor", "")
            if name == "Merger":
                self.root.after(0, self.update_progress, 1.0, "Uniendo audio y vídeo",
                                "El archivo final puede tardar un poco.")

    def update_progress(self, ratio, status, detail):
        if not self.is_downloading:
            return
        self.progress.set(ratio)
        self.status_text.set(status)
        self.detail_text.set(detail)

    def finish(self, success, message):
        self.is_downloading = False
        self.action_button.configure(text="Descargar", bg=ACCENT, activebackground=ACCENT_DEEP,
                                     fg="#FFFFFF", activeforeground="#FFFFFF")
        if success:
            self.progress.set(1.0)
            self.status_text.set(message)
            location = os.path.dirname(self.last_file) if self.last_file else self.output_dir.get()
            self.detail_text.set("El archivo está listo para verlo o moverlo.")
            self.location_text.set(f"Guardado en {location}")
            if not self.location.winfo_manager():
                self.location.pack(fill="x", pady=(8, 0))
            self.open_button.pack(side="right")
        else:
            self.status_text.set(message)
            self.location.pack_forget()
            self.location_text.set("")
            if self.cancelled:
                self.detail_text.set("No se guardó ningún archivo nuevo.")
            elif "Falta yt-dlp" in message:
                self.detail_text.set("Usa el .exe de la release o instala requirements.txt.")
            else:
                self.detail_text.set("Revisa el enlace y la conexión, y vuelve a intentarlo.")
            self.progress.set(0)

    def open_folder(self):
        folder = self.output_dir.get()
        if self.last_file:
            folder = os.path.dirname(self.last_file)
        try:
            if sys.platform == "win32":
                os.startfile(folder)
            else:
                webbrowser.open(Path(folder).as_uri())
        except Exception:
            self.detail_text.set(f"Carpeta: {folder}")


def main():
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

    root = tk.Tk()
    TwitchDownloaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
