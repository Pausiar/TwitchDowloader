import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import re
import sys

# Instalar yt-dlp si no está disponible
try:
    import yt_dlp
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    import yt_dlp

class TwitchDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Twitch VOD Downloader")
        self.root.geometry("600x400")
        self.root.resizable(True, True)

        # Icono de la ventana
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.ico")
            self.root.iconbitmap(icon_path)
        except Exception:
            pass
        
        # Variables
        self.url_var = tk.StringVar()
        self.output_dir = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.status_var = tk.StringVar(value="Listo para descargar")
        self.progress_var = tk.StringVar(value="")
        self.is_downloading = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="🎮 Twitch VOD Downloader", font=("Segoe UI", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Frame para URL
        url_frame = ttk.LabelFrame(main_frame, text="Link del VOD de Twitch", padding="10")
        url_frame.pack(fill=tk.X, pady=(0, 15))
        
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, font=("Segoe UI", 11))
        url_entry.pack(fill=tk.X, pady=5)
        url_entry.bind('<Return>', lambda e: self.start_download())
        
        # Ejemplo de URL
        example_label = ttk.Label(url_frame, text="Ejemplo: https://www.twitch.tv/videos/123456789", 
                                  font=("Segoe UI", 9), foreground="gray")
        example_label.pack(anchor=tk.W)
        
        # Frame para directorio de salida
        output_frame = ttk.LabelFrame(main_frame, text="Carpeta de destino", padding="10")
        output_frame.pack(fill=tk.X, pady=(0, 15))
        
        output_inner = ttk.Frame(output_frame)
        output_inner.pack(fill=tk.X)
        
        output_entry = ttk.Entry(output_inner, textvariable=self.output_dir, font=("Segoe UI", 10))
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(output_inner, text="Examinar...", command=self.browse_folder)
        browse_btn.pack(side=tk.RIGHT)
        
        # Botón de descarga
        self.download_btn = ttk.Button(main_frame, text="⬇️ Descargar en Máxima Calidad", 
                                        command=self.start_download, style="Accent.TButton")
        self.download_btn.pack(pady=15, ipadx=20, ipady=10)
        
        # Frame de progreso
        progress_frame = ttk.LabelFrame(main_frame, text="Progreso", padding="10")
        progress_frame.pack(fill=tk.BOTH, expand=True)
        
        # Barra de progreso
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Estado
        status_label = ttk.Label(progress_frame, textvariable=self.status_var, font=("Segoe UI", 10))
        status_label.pack(anchor=tk.W)
        
        # Progreso detallado
        progress_label = ttk.Label(progress_frame, textvariable=self.progress_var, 
                                   font=("Consolas", 9), foreground="blue")
        progress_label.pack(anchor=tk.W, pady=(5, 0))
        
    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.output_dir.get())
        if folder:
            self.output_dir.set(folder)
            
    def validate_url(self, url):
        """Valida que sea una URL de Twitch válida"""
        twitch_patterns = [
            r'https?://(www\.)?twitch\.tv/videos/\d+',
            r'https?://(www\.)?twitch\.tv/\w+/video/\d+',
            r'https?://(www\.)?twitch\.tv/\w+/clip/\w+',
            r'https?://clips\.twitch\.tv/\w+',
        ]
        return any(re.match(pattern, url) for pattern in twitch_patterns)
    
    def start_download(self):
        if self.is_downloading:
            messagebox.showwarning("Aviso", "Ya hay una descarga en progreso")
            return
            
        url = self.url_var.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Por favor ingresa un link de Twitch")
            return
            
        if not self.validate_url(url):
            messagebox.showerror("Error", "El link no parece ser un VOD o clip válido de Twitch\n\n"
                               "Formatos válidos:\n"
                               "• https://www.twitch.tv/videos/123456789\n"
                               "• https://clips.twitch.tv/ClipName")
            return
            
        output_dir = self.output_dir.get()
        if not os.path.exists(output_dir):
            messagebox.showerror("Error", "La carpeta de destino no existe")
            return
            
        # Iniciar descarga en un hilo separado
        self.is_downloading = True
        self.download_btn.config(state=tk.DISABLED)
        self.progress_bar.start(10)
        self.status_var.set("Iniciando descarga...")
        
        thread = threading.Thread(target=self.download_video, args=(url, output_dir))
        thread.daemon = True
        thread.start()
        
    def download_video(self, url, output_dir):
        try:
            # Configuración de yt-dlp
            ydl_opts = {
                'format': 'best',  # Mejor calidad disponible
                'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
                'noplaylist': True,
                'progress_hooks': [self.progress_hook],
            }
            
            self.root.after(0, lambda: self.status_var.set("Obteniendo información del video..."))
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.root.after(0, self.download_complete, True, "¡Descarga completada exitosamente!")
                
        except Exception as e:
            self.root.after(0, self.download_complete, False, f"Error: {str(e)}")
    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            msg = f"{percent} - Velocidad: {speed} - Tiempo restante: {eta}"
            self.root.after(0, lambda m=msg: self.progress_var.set(m))
            self.root.after(0, lambda: self.status_var.set("Descargando..."))
        elif d['status'] == 'finished':
            self.root.after(0, lambda: self.progress_var.set("Procesando archivo..."))
            self.root.after(0, lambda: self.status_var.set("Finalizando..."))
            
    def download_complete(self, success, message):
        self.is_downloading = False
        self.download_btn.config(state=tk.NORMAL)
        self.progress_bar.stop()
        self.status_var.set(message)
        
        if success:
            self.progress_var.set("")
            messagebox.showinfo("Éxito", f"¡Descarga completada!\n\nArchivo guardado en:\n{self.output_dir.get()}")
        else:
            messagebox.showerror("Error", message)


def main():
    root = tk.Tk()
    
    # Configurar estilo
    style = ttk.Style()
    try:
        style.theme_use('vista')  # Tema moderno en Windows
    except:
        pass
        
    app = TwitchDownloader(root)
    root.mainloop()


if __name__ == "__main__":
    main()
