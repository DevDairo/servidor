import os
import requests
from PIL import Image
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TPE2, TALB, TDRC, TCON

import config
from services.cleaner import clean_filename


# ── Carátulas ────────────────────────────────────────────────────────────────

def process_cover(download_info: dict) -> str | None:
    """
    Convierte el thumbnail .webp a .jpg y lo guarda en la carpeta de portadas.
    Si el .webp no existe, lo descarga desde la URL de respaldo de yt-dlp.

    Devuelve la ruta absoluta al .jpg, o None si no se pudo obtener.
    """
    safe_name = clean_filename(download_info["title"])
    cover_path = os.path.join(config.COVERS_DIR, f"{safe_name}.jpg")

    webp_path = download_info["webp"]
    fallback_url = download_info["info_dict"].get("thumbnail")

    if _convert_webp(webp_path, cover_path):
        return cover_path

    if fallback_url and _download_cover(fallback_url, cover_path):
        return cover_path

    print("[!] No se pudo obtener la carátula.")
    return None


def _convert_webp(webp_path: str, jpg_path: str) -> bool:
    try:
        if not os.path.exists(webp_path):
            return False
        with Image.open(webp_path) as im:
            im.convert("RGB").save(jpg_path, "jpeg")
        print(f"[✓] Carátula convertida desde .webp")
        return True
    except Exception as e:
        print(f"[!] Error al convertir .webp: {e}")
        return False


def _download_cover(url: str, jpg_path: str) -> bool:
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(jpg_path, "wb") as f:
                f.write(response.content)
            print(f"[✓] Carátula descargada desde URL")
            return True
    except Exception as e:
        print(f"[!] Error al descargar carátula: {e}")
    return False


# ── Metadatos ID3 ─────────────────────────────────────────────────────────────

def insert_metadata(mp3_path: str, cover_path: str | None,
                    title: str, info_dict: dict) -> bool:
    """
    Inserta etiquetas ID3 y la carátula en el archivo MP3.
    Devuelve True si tuvo éxito, False si falló.
    """
    if not os.path.exists(mp3_path):
        print("[X] El archivo MP3 no existe, no se pueden insertar metadatos.")
        return False

    try:
        artist = info_dict.get("uploader", "Artista Desconocido")
        album  = info_dict.get("album", "YouTube")
        year   = info_dict.get("upload_date", "2024")[:4]

        audio = ID3(mp3_path)
        audio.delete()

        audio.add(TIT2(encoding=3, text=title))
        audio.add(TPE1(encoding=3, text=artist))
        audio.add(TPE2(encoding=3, text=artist))
        audio.add(TALB(encoding=3, text=album))
        audio.add(TDRC(encoding=3, text=year))
        audio.add(TCON(encoding=3, text="Varios"))

        if cover_path and os.path.exists(cover_path):
            with open(cover_path, "rb") as img:
                audio.add(APIC(
                    encoding=3, mime="image/jpeg",
                    type=3, desc="Portada", data=img.read()
                ))

        audio.save(v2_version=3)
        print("[✓] Metadatos insertados correctamente.")

        # Limpiar el .webp temporal
        webp_path = mp3_path.replace(".mp3", ".webp")
        if os.path.exists(webp_path):
            os.remove(webp_path)

        return True

    except Exception as e:
        print(f"[X] Error al insertar metadatos: {e}")
        return False
