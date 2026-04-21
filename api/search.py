from flask import Blueprint, jsonify, request
from services.downloader import search_videos

search_bp = Blueprint("search", __name__)


@search_bp.get("/api/search")
def search():
    """
    Busca canciones en YouTube.

    Query param:
        q (str) — texto de búsqueda, requerido

    Respuesta 200:
        { "results": [ { id, url, title, artist, thumbnail }, … ] }
    """
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "El parámetro 'q' es requerido."}), 400

    results = search_videos(query)
    return jsonify({"results": results})
