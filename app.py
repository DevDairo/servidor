from flask import Flask
from flask_cors import CORS

import config
from database.db import init_db
from api.search import search_bp
from api.download import download_bp
from api.library import library_bp

app = Flask(__name__)

# Permite peticiones desde cualquier origen (necesario para Android)
CORS(app)

# Registrar blueprints
app.register_blueprint(search_bp)
app.register_blueprint(download_bp)
app.register_blueprint(library_bp)


if __name__ == "__main__":
    init_db()
    print(f"[✓] Servidor iniciado en http://{config.HOST}:{config.PORT}")
    print(f"[✓] Música en:   {config.MUSIC_DIR}")
    print(f"[✓] Base de datos: {config.DATABASE_PATH}")
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
