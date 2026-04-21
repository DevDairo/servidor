import os
from flask import Blueprint, jsonify, send_file, abort, url_for
from database.models import get_all_songs

library_bp = Blueprint("library", __name__)


@library_bp.get("/api/library")
def library():
    """
    Devuelve la lista de canciones descargadas.

    Respuesta 200:
        { "songs": [ { id, title, artist, mp3_url, cover_url, created_at }, … ] }
    """
    songs = get_all_songs()

    for song in songs:
        filename = os.path.basename(song["file_path"])
        song["mp3_url"]   = url_for("library.serve_file",
                                    filename=filename, _external=True)
        song["cover_url"] = url_for("library.serve_cover",
                                    filename=filename, _external=True)
        # No exponer rutas internas del servidor
        del song["file_path"]
        del song["cover_path"]

    return jsonify({"songs": songs})


@library_bp.get("/api/files/<path:filename>")
def serve_file(filename: str):
    """
    Sirve un archivo MP3 para que Android lo descargue.
    Soporta Range requests (necesario para streaming parcial en Android).
    """
    from config import MUSIC_DIR
    file_path = os.path.join(MUSIC_DIR, filename)

    if not os.path.exists(file_path):
        abort(404)

    return send_file(
        file_path,
        mimetype="audio/mpeg",
        as_attachment=False,
        conditional=True,   # Habilita Range requests
    )


@library_bp.get("/api/covers/<path:filename>")
def serve_cover(filename: str):
    """
    Sirve la carátula de una canción extrayéndola del MP3.
    Mismo mecanismo que en el proyecto web original.
    """
    import mutagen
    from flask import Response
    from config import MUSIC_DIR

    mp3_name  = filename.rsplit(".", 1)[0] + ".mp3"
    mp3_path  = os.path.join(MUSIC_DIR, mp3_name)

    if not os.path.exists(mp3_path):
        abort(404)

    try:
        audio = mutagen.File(mp3_path)
        if audio and hasattr(audio, "tags"):
            for key in audio.tags:
                if key.startswith("APIC"):
                    return Response(audio.tags[key].data, mimetype="image/jpeg")
    except Exception as e:
        print(f"[!] Error al extraer carátula: {e}")

    abort(404)
