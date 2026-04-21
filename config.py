import os

# --- Rutas base ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
MUSIC_DIR = os.path.join(STATIC_DIR, "musica")
COVERS_DIR = os.path.join(STATIC_DIR, "portadas")
DATABASE_PATH = os.path.join(BASE_DIR, "database", "musicflow.db")

# --- Servidor ---
HOST = "0.0.0.0"
PORT = 5001  # Puerto distinto al proyecto web (5000) para no colisionar
DEBUG = True

# --- Descarga ---
DEFAULT_QUALITY = "320"
MAX_SEARCH_RESULTS = 15

# --- Crear carpetas si no existen ---
os.makedirs(MUSIC_DIR, exist_ok=True)
os.makedirs(COVERS_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
