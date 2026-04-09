# 🎮 Twitch VOD Downloader

Aplicación sencilla para descargar VODs y clips de Twitch en la máxima calidad disponible.

## 📋 Requisitos

- Python 3.8 o superior
- yt-dlp

## 🚀 Instalación

1. Instala las dependencias:
```bash
pip install -r requirements.txt
```

2. Ejecuta la aplicación:
```bash
python twitch_downloader.py
```

## 📖 Uso

1. Copia el link del VOD o clip de Twitch
2. Pégalo en la aplicación
3. Selecciona la carpeta donde quieres guardar el video
4. Haz clic en "Descargar en Máxima Calidad"

## 🔗 Links soportados

- VODs: `https://www.twitch.tv/videos/123456789`
- Clips: `https://clips.twitch.tv/ClipName`

## ⚙️ Características

- ✅ Descarga en la máxima calidad disponible
- ✅ Interfaz gráfica sencilla
- ✅ Barra de progreso
- ✅ Soporte para VODs y clips

## 🪟 Ejecutable para Windows (.exe)

Este repositorio genera automáticamente un ejecutable de Windows en GitHub Releases.

### Cómo publicar una nueva versión

1. Sube tus cambios a `main`.
2. Crea y sube un tag con formato `vX.Y.Z`.

```bash
git tag v1.0.0
git push origin v1.0.0
```

3. GitHub Actions compilará el `.exe` en Windows y lo publicará en Releases.

### Descarga

Ve a la sección **Releases** del repositorio y descarga `TwitchDownloader.exe` desde la última versión.
