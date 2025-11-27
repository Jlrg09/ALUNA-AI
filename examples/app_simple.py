"""
Aplicación principal simplificada sin dependencias problemáticas
"""
from flask import Flask, render_template, request, jsonify
import os
import json

# Configuración básica
app = Flask(__name__)
app.config['SECRET_KEY'] = 'origen-ai-key-2024'

# Configuración de archivos
KNOWLEDGE_DIR = "documentos"
EMBEDDINGS_FILE = "embeddings.pkl"

# Configuración de ORIGEN
ORIGEN_CONFIG = {
    "name": "ORIGEN",
    "subtitle": "Memoria de la Sierra • Tecnología Viva",
    "welcome_message": "¡Wintukua! Soy ORIGEN 🏔️✨",
    "welcome_description": "Soy una inteligencia artificial de la Universidad del Magdalena."
}

@app.route("/")
def home():
    """Página principal"""
    return render_template('aluna_chat.html', config=ORIGEN_CONFIG)

@app.route("/api/chat", methods=["POST"])
def chat():
    """Endpoint básico de chat"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({"error": "No se proporcionó ninguna pregunta"}), 400
        
        # Respuesta básica sin IA por ahora
        response = f"Recibí tu pregunta: '{question}'. El sistema está configurado correctamente."
        
        return jsonify({"answer": response})
        
    except Exception as e:
        return jsonify({"error": f"Error procesando la solicitud: {str(e)}"}), 500

@app.route("/api/status")
def status():
    """Estado del sistema"""
    return jsonify({
        "status": "ok",
        "message": "ORIGEN funcionando correctamente",
        "documents_dir_exists": os.path.exists(KNOWLEDGE_DIR),
        "embeddings_exists": os.path.exists(EMBEDDINGS_FILE)
    })

@app.route("/api/documents")
def list_documents():
    """Lista los documentos disponibles"""
    if not os.path.exists(KNOWLEDGE_DIR):
        return jsonify({"documents": [], "message": "Directorio de documentos no existe"})
    
    documents = []
    for filename in os.listdir(KNOWLEDGE_DIR):
        if filename.endswith(('.pdf', '.txt', '.docx')):
            filepath = os.path.join(KNOWLEDGE_DIR, filename)
            size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
            documents.append({
                "filename": filename,
                "size": size
            })
    
    return jsonify({"documents": documents, "count": len(documents)})

if __name__ == "__main__":
    print("🚀 Iniciando ORIGEN (Versión Simplificada)")
    print("🌐 Accede a: http://localhost:5000")
    print("-" * 50)
    
    # Crear directorio de documentos si no existe
    os.makedirs(KNOWLEDGE_DIR, exist_ok=True)
    
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
