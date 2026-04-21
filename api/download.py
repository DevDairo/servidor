from flask import Blueprint, jsonify, request
from database.models import get_task
from services.queue_manager import queue_manager

download_bp = Blueprint("download", __name__)


@download_bp.post("/api/download")
def download():
    """
    Encola la descarga de una canción.

    Body JSON:
        { "url": "https://www.youtube.com/watch?v=..." }

    Respuesta 200:
        { "task_id": "<uuid>" }
    """
    body = request.get_json(silent=True) or {}
    url = body.get("url", "").strip()

    if not url:
        return jsonify({"error": "El campo 'url' es requerido."}), 400

    task_id = queue_manager.enqueue(url)
    return jsonify({"task_id": task_id})


@download_bp.get("/api/status/<task_id>")
def status(task_id: str):
    """
    Devuelve el estado actual de una tarea de descarga.

    Respuesta 200:
        { "task_id", "status", "message", "progress" }

    Valores de status:
        queued       — esperando en cola
        downloading  — descargando audio
        processing   — convirtiendo / insertando metadatos
        done         — completado
        error        — falló
    """
    task = get_task(task_id)

    if not task:
        return jsonify({"error": "Tarea no encontrada."}), 404

    return jsonify(task)
