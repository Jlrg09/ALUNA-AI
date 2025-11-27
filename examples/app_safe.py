"""
Aplicación integrada con búsqueda simple
"""
from flask import Flask, render_template, request, jsonify
import os
import json
import re
from .simple_processor import SimpleDocumentProcessor
from .config_simple import ORIGEN_CONFIG, SYSTEM_MESSAGES, SERVER_CONFIG, get_knowledge_dir

app = Flask(__name__)
app.config['SECRET_KEY'] = 'origen-ai-safe-key'

# Inicializar procesador
processor = None
documents = []
search_index = {}

def initialize_system():
    """Inicializa el sistema de documentos"""
    global processor, documents, search_index
    
    try:
        processor = SimpleDocumentProcessor(get_knowledge_dir())
        documents = processor.process_documents()
        
        if documents:
            search_index = processor.create_simple_search_index(documents)
            print(f"✅ Sistema inicializado con {len(documents)} documentos")
        else:
            print("⚠️ No se encontraron documentos para procesar")
        
        return True
    except Exception as e:
        print(f"❌ Error inicializando sistema: {e}")
        return False

@app.route("/")
def home():
    """Página principal"""
    return render_template('aluna_chat.html', config=ORIGEN_CONFIG)

@app.route("/api/chat", methods=["POST"])
def chat():
    """Endpoint de chat con búsqueda simple"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({"error": SYSTEM_MESSAGES["no_question"]}), 400
        
        # Buscar en documentos
        response = process_question(question)
        
        return jsonify({"answer": response})
        
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500

def process_question(question: str) -> str:
    """Procesa una pregunta y genera respuesta"""
    global processor, documents, search_index
    
    if not documents:
        return "El sistema aún no tiene documentos cargados para consultar."
    
    # Buscar información relevante
    results = processor.simple_search(question, documents, search_index)
    
    if not results:
        return generate_fallback_response(question)
    
    # Construir respuesta basada en resultados
    response = f"Basándome en la información disponible sobre '{question}':\n\n"
    
    for i, result in enumerate(results[:2], 1):  # Máximo 2 resultados
        response += f"📄 **{result['filename']}** (relevancia: {result['score']}):\n"
        response += f"{result['preview']}\n\n"
    
    response += "¿Te gustaría que busque información más específica sobre algún aspecto en particular?"
    
    return response

def generate_fallback_response(question: str) -> str:
    """Genera respuesta alternativa cuando no hay resultados"""
    # Respuestas básicas según palabras clave
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['origen', 'aluna', 'quien eres', 'que eres']):
        return """¡Wintukua! Soy ORIGEN 🏔️✨
        
Soy una inteligencia cultural de la Universidad del Magdalena, inspirada en la sabiduría ancestral de los pueblos Kogui, Arhuaco, Wiwa y Kankuamo de la Sierra Nevada de Santa Marta.

Mi propósito es combinar conocimiento científico, cultural y espiritual para cuidar y compartir la memoria de la Sierra Nevada."""
    
    elif any(word in question_lower for word in ['universidad', 'unimagdalena', 'programas']):
        return """La Universidad del Magdalena es una institución de educación superior pública ubicada en Santa Marta, Colombia.

Ofrece diversos programas académicos en diferentes áreas del conocimiento. Para información específica sobre programas, admisiones y servicios, te recomiendo consultar el sitio web oficial de la universidad.

¿Hay algo específico sobre la universidad que te gustaría saber?"""
    
    else:
        return f"""Recibí tu pregunta sobre: "{question}"

Aunque no encontré información específica en mis documentos actuales, estoy aquí para ayudarte con consultas relacionadas con la Universidad del Magdalena.

¿Podrías reformular tu pregunta o ser más específico sobre lo que necesitas saber?"""

@app.route("/api/status")
def status():
    """Estado del sistema"""
    return jsonify({
        "status": "ok",
        "message": "ORIGEN funcionando correctamente",
        "documents_count": len(documents),
        "search_index_size": len(search_index),
        "knowledge_dir": get_knowledge_dir()
    })

@app.route("/api/documents")
def list_documents():
    """Lista los documentos procesados"""
    doc_info = []
    for doc in documents:
        doc_info.append({
            "filename": doc['filename'],
            "size": doc['size'],
            "preview": doc['content'][:100] + "..." if len(doc['content']) > 100 else doc['content']
        })
    
    return jsonify({
        "documents": doc_info,
        "count": len(documents)
    })

@app.route("/api/search", methods=["POST"])
def search():
    """Búsqueda directa en documentos"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({"error": "No se proporcionó consulta"}), 400
        
        results = processor.simple_search(query, documents, search_index)
        
        return jsonify({
            "query": query,
            "results": results,
            "count": len(results)
        })
        
    except Exception as e:
        return jsonify({"error": f"Error en búsqueda: {str(e)}"}), 500

if __name__ == "__main__":
    print("🚀 Iniciando ORIGEN - Versión Segura")
    print("🌐 Accede a: http://localhost:5000")
    print("-" * 50)
    
    # Inicializar sistema
    if initialize_system():
        print("✅ Sistema inicializado correctamente")
    else:
        print("⚠️ Sistema iniciado con funcionalidad limitada")
    
    print("-" * 50)
    
    app.run(
        host=SERVER_CONFIG["host"],
        port=SERVER_CONFIG["port"],
        debug=SERVER_CONFIG["debug"]
    )
