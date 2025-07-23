import os
from flask import jsonify

# Rutas desde variables de entorno o valores por defecto
EMBEDDINGS_FILE = os.getenv("EMBEDDINGS_FILE", "embeddings.pkl")
KNOWLEDGE_DIR = os.getenv("KNOWLEDGE_DIR", "documentos")
HASHES_FILE = os.path.join(KNOWLEDGE_DIR, "hashes.txt")

def registrar_ruta_reset(app):

    @app.route("/api/reset_embeddings", methods=["POST"])
    def reset_embeddings():
        mensajes = []

        # Borrar archivo de embeddings
        if os.path.exists(EMBEDDINGS_FILE):
            try:
                os.remove(EMBEDDINGS_FILE)
                mensajes.append("✅ Archivo de embeddings eliminado.")
            except Exception as e:
                return jsonify({"error": f"❌ No se pudo eliminar el archivo de embeddings: {e}"}), 500
        else:
            mensajes.append("⚠️ No se encontró el archivo de embeddings.")

        # Borrar archivo de hashes (para permitir recarga de documentos)
        if os.path.exists(HASHES_FILE):
            try:
                os.remove(HASHES_FILE)
                mensajes.append("✅ Archivo de hashes eliminado.")
            except Exception as e:
                return jsonify({"error": f"❌ No se pudo eliminar el archivo de hashes: {e}"}), 500
        else:
            mensajes.append("⚠️ No se encontró el archivo de hashes.")

        return jsonify({"message": "Embeddings reiniciados correctamente.", "detalles": mensajes}), 200
