from database.db import get_connection


# ── Tareas ────────────────────────────────────────────────────────────────────

def create_task(task_id: str, youtube_url: str):
    """Inserta una tarea nueva en estado 'queued'."""
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO tasks (task_id, status, message, progress, youtube_url)
        VALUES (?, 'queued', 'En cola', 0, ?)
        """,
        (task_id, youtube_url),
    )
    conn.commit()
    conn.close()


def update_task(task_id: str, status: str, message: str, progress: float = 0):
    """Actualiza el estado de una tarea existente."""
    conn = get_connection()
    conn.execute(
        """
        UPDATE tasks
        SET status = ?, message = ?, progress = ?,
            updated_at = datetime('now')
        WHERE task_id = ?
        """,
        (status, message, progress, task_id),
    )
    conn.commit()
    conn.close()


def finish_task(task_id: str, song_id: int):
    """Marca la tarea como completada y la vincula a la canción creada."""
    conn = get_connection()
    conn.execute(
        """
        UPDATE tasks
        SET status = 'done', message = '¡Descarga completa!',
            progress = 100, song_id = ?, updated_at = datetime('now')
        WHERE task_id = ?
        """,
        (song_id, task_id),
    )
    conn.commit()
    conn.close()


def fail_task(task_id: str, error: str):
    """Marca la tarea como fallida con el mensaje de error."""
    conn = get_connection()
    conn.execute(
        """
        UPDATE tasks
        SET status = 'error', message = ?,
            updated_at = datetime('now')
        WHERE task_id = ?
        """,
        (error[:300], task_id),  # Limita el mensaje para no saturar la DB
    )
    conn.commit()
    conn.close()


def get_task(task_id: str) -> dict | None:
    """Devuelve el estado de una tarea como diccionario, o None si no existe."""
    conn = get_connection()
    row = conn.execute(
        "SELECT task_id, status, message, progress FROM tasks WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


# ── Canciones ─────────────────────────────────────────────────────────────────

def save_song(title: str, artist: str, youtube_url: str,
              file_path: str, cover_path: str) -> int:
    """
    Inserta una canción nueva y devuelve su ID.
    Si la URL ya existe, devuelve el ID existente sin duplicar.
    """
    conn = get_connection()

    existing = conn.execute(
        "SELECT id FROM songs WHERE youtube_url = ?", (youtube_url,)
    ).fetchone()

    if existing:
        conn.close()
        return existing["id"]

    cursor = conn.execute(
        """
        INSERT INTO songs (title, artist, youtube_url, file_path, cover_path)
        VALUES (?, ?, ?, ?, ?)
        """,
        (title, artist, youtube_url, file_path, cover_path),
    )
    song_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return song_id


def get_all_songs() -> list[dict]:
    """Devuelve todas las canciones ordenadas por fecha de descarga, más reciente primero."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, title, artist, file_path, cover_path, created_at FROM songs ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def song_exists(youtube_url: str) -> bool:
    """Comprueba si una URL de YouTube ya fue descargada."""
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM songs WHERE youtube_url = ?", (youtube_url,)
    ).fetchone()
    conn.close()
    return row is not None
