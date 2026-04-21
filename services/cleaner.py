import re
import unicodedata


def clean_filename(filename: str) -> str:
    """
    Limpia un nombre de archivo eliminando caracteres inválidos
    y normalizando texto (acentos, espacios, etc.).
    """

    if not filename:
        return "audio"

    # 1. Normalizar acentos (á -> a, ñ -> n, etc.)
    filename = unicodedata.normalize("NFKD", filename)
    filename = filename.encode("ascii", "ignore").decode("ascii")

    # 2. Eliminar caracteres inválidos en sistemas de archivos
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)

    # 3. Reemplazar espacios múltiples por uno solo
    filename = re.sub(r'\s+', ' ', filename).strip()

    # 4. Reemplazar espacios por guiones (opcional pero recomendado)
    filename = filename.replace(" ", "_")

    # 5. Limitar longitud (evita problemas en Windows)
    return filename[:100]