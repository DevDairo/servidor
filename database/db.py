import sqlite3
import config


def get_connection():
    """
    Devuelve una conexión a la base de datos SQLite.
    check_same_thread=False es necesario porque Flask puede
    usar la conexión desde hilos distintos.
    """
    conn = sqlite3.connect(config.DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Permite acceder a columnas por nombre
    return conn


def init_db():
    """
    Crea las tablas si no existen. Se llama una sola vez al iniciar el servidor.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL,
            artist      TEXT    NOT NULL DEFAULT 'Artista Desconocido',
            youtube_url TEXT    NOT NULL,
            file_path   TEXT    NOT NULL,
            cover_path  TEXT,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id     TEXT    PRIMARY KEY,
            status      TEXT    NOT NULL DEFAULT 'queued',
            message     TEXT    NOT NULL DEFAULT 'En cola',
            progress    REAL    NOT NULL DEFAULT 0,
            youtube_url TEXT    NOT NULL,
            song_id     INTEGER REFERENCES songs(id),
            created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
            updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()
    print("[✓] Base de datos inicializada.")
