import queue
import threading
import uuid

from database import models
from services import downloader, metadata


class QueueManager:
    """
    Gestiona una cola de descargas de una tarea a la vez.
    Usa un hilo daemon para procesar en segundo plano sin bloquear Flask.
    """

    def __init__(self):
        self._queue = queue.Queue()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    # ── Interfaz pública ──────────────────────────────────────────────────────

    def enqueue(self, youtube_url: str) -> str:
        """
        Agrega una URL a la cola y devuelve el task_id para hacer seguimiento.
        Si la URL ya fue descargada, lo indica en la tarea sin volver a descargar.
        """
        task_id = str(uuid.uuid4())
        models.create_task(task_id, youtube_url)

        if models.song_exists(youtube_url):
            models.update_task(task_id, "done",
                               "Ya descargada previamente.", 100)
        else:
            self._queue.put((task_id, youtube_url))

        return task_id

    # ── Worker interno ────────────────────────────────────────────────────────

    def _worker(self):
        """Procesa tareas de la cola de forma secuencial."""
        while True:
            task_id, url = self._queue.get()
            try:
                self._process(task_id, url)
            except Exception as e:
                models.fail_task(task_id, str(e))
            finally:
                self._queue.task_done()

    def _process(self, task_id: str, url: str):
        # 1. Descarga
        models.update_task(task_id, "downloading", "Conectando con YouTube…", 0)

        def progress_hook(d):
            if d["status"] == "downloading":
                raw = d.get("_percent_str", "0%").replace("%", "").strip()
                try:
                    pct = float(raw)
                    models.update_task(
                        task_id, "downloading",
                        f"Descargando… {int(pct)}%", pct
                    )
                except ValueError:
                    pass

        result = downloader.download_audio(url, progress_hook=progress_hook)
        if not result:
            raise RuntimeError("Falló la descarga del audio.")

        # 2. Carátula
        models.update_task(task_id, "processing", "Procesando carátula…", 100)
        cover_path = metadata.process_cover(result)

        # 3. Metadatos
        models.update_task(task_id, "processing", "Insertando metadatos…", 100)
        ok = metadata.insert_metadata(
            mp3_path=result["mp3"],
            cover_path=cover_path,
            title=result["title"],
            info_dict=result["info_dict"],
        )
        if not ok:
            raise RuntimeError("Falló la inserción de metadatos.")

        # 4. Guardar en DB
        artist = result["info_dict"].get("uploader", "Artista Desconocido")
       
        song_id = models.save_song(
            title=result["title"],
            artist=artist,
            youtube_url=url,
            file_path=result["mp3"],
            cover_path="",   # La carátula vive incrustada en el MP3, no en disco
        )
        models.finish_task(task_id, song_id)
        print(f"[✓] Tarea {task_id[:8]}… completada.")


# Instancia única compartida por toda la app
queue_manager = QueueManager()
