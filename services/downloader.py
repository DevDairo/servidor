import os
import yt_dlp

import config
from services.cleaner import clean_filename


def search_videos(query: str) -> list[dict]:
    """
    Busca videos en YouTube y devuelve una lista de resultados formateados.
    """
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "force_generic_extractor": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(
                f"ytsearch{config.MAX_SEARCH_RESULTS}:{query}", download=False
            )

        videos = []
        for video in result.get("entries", []):
            video_id = video.get("id")
            if not video_id:
                continue
            videos.append({
                "id":        video_id,
                "url":       f"https://www.youtube.com/watch?v={video_id}",
                "title":     video.get("title", "Título desconocido"),
                "artist":    video.get("uploader", "Artista desconocido"),
                "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
            })
        return videos

    except Exception as e:
        print(f"[X] Error en búsqueda: {e}")
        return []


def download_audio(url: str, progress_hook=None) -> dict | None:
    """
    Descarga el audio de una URL de YouTube como MP3.

    Devuelve un diccionario con:
        mp3        — ruta absoluta al archivo MP3
        webp       — ruta al thumbnail descargado (puede no existir)
        title      — título original del video
        info_dict  — diccionario completo de metadatos de yt-dlp

    Devuelve None si la descarga falla.
    """
    # Obtener metadatos sin descargar primero
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except Exception as e:
            print(f"[X] No se pudo obtener información del video: {e}")
            return None

    title = info.get("title", "descarga")
    safe_name = clean_filename(title)
    base_path = os.path.join(config.MUSIC_DIR, safe_name)

    ydl_opts = {
    "format": "bestaudio/best",          # Siempre el mejor audio disponible
    "outtmpl": f"{base_path}.%(ext)s",
    "writethumbnail": True,
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "0",     # VBR máxima calidad (equivale a ~320kbps)
        },
        {"key": "FFmpegMetadata"},
    ],
    "quiet": True,
    "progress_hooks": [progress_hook] if progress_hook else [],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except Exception as e:
            print(f"[X] Error durante la descarga: {e}")
            return None

    return {
        "mp3":       f"{base_path}.mp3",
        "webp":      f"{base_path}.webp",
        "title":     title,
        "info_dict": info,
    }