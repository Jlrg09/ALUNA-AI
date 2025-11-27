"""
Módulo para reiniciar embeddings y datos relacionados.

Dos usos:
1) Como ruta Flask: expone POST /api/reset_embeddings para borrar archivos de embeddings y memoria.
   Usar: from scripts.reset_embeddings import registrar_ruta_reset; registrar_ruta_reset(app)
2) Como script CLI: ejecuta una petición POST a esa ruta en localhost.
"""
import os
from typing import Dict, Any

from flask import jsonify

# CLI helper (solo se importa si se ejecuta como script)
try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # Disponible solo para uso CLI

from config import EMBEDDINGS_FILE, MEMORY_FILE


def _safe_remove(path: str) -> bool:
    """Elimina un archivo si existe. Devuelve True si se eliminó."""
    if not path:
        return False
    try:
        if os.path.exists(path):
            os.remove(path)
            return True
    except Exception:
        return False
    return False


def registrar_ruta_reset(app) -> None:
    """Registra la ruta Flask para reiniciar embeddings/memoria.

    Ruta: POST /api/reset_embeddings
    Respuesta: { removed: {embeddings: bool, memory: bool}, files: {embeddings: str, memory: str} }
    """
    @app.route("/api/reset_embeddings", methods=["POST"])
    def reset_embeddings_route():  # type: ignore
        removed_embeddings = _safe_remove(EMBEDDINGS_FILE)
        removed_memory = _safe_remove(MEMORY_FILE)

        result: Dict[str, Any] = {
            "removed": {
                "embeddings": removed_embeddings,
                "memory": removed_memory,
            },
            "files": {
                "embeddings": EMBEDDINGS_FILE or "",
                "memory": MEMORY_FILE or "",
            },
        }
        status = 200
        return jsonify(result), status


def main():
    """Ejecuta el reset vía HTTP contra un servidor local en ejecución."""
    if requests is None:
        print("El módulo 'requests' no está disponible en este entorno.")
        return
    try:
        resp = requests.post("http://localhost:5000/api/reset_embeddings", timeout=10)
        print(resp.status_code, resp.json())
    except Exception as e:
        print("Error llamando a /api/reset_embeddings:", e)


if __name__ == "__main__":
    main()
