"""
Rutas de la API para el chat
"""
from flask import Blueprint, request, jsonify
from models import ChatRequest
from services.chat_service import ChatService

# Crear blueprint para las rutas de chat
chat_bp = Blueprint('chat', __name__)

# Instancia global del servicio de chat (se inicializa una vez)
chat_service = None


def init_chat_service():
    """Inicializa el servicio de chat si no existe"""
    global chat_service
    if chat_service is None:
        chat_service = ChatService()
    return chat_service


@chat_bp.route("/api/chat", methods=["POST"])
def chat():
    """
    Endpoint principal para el chat
    
    Acepta:
    {
        "question": "string",
        "session_id": "string?"  // opcional para historial persistente
    }
    
    Retorna:
    {
        "answer": "string"
    }
    """
    try:
        # Obtener datos de la solicitud
        data = request.get_json(force=True)
        chat_request = ChatRequest.from_json(data)
        
        # Validar solicitud
        if not chat_request.question:
            return jsonify({"answer": "Por favor, escribe tu pregunta."})
        
        # Inicializar servicio si es necesario
        service = init_chat_service()
        
        # Procesar solicitud
        response = service.process_chat_request(chat_request)
        
        return jsonify(response.to_dict())
        
    except Exception as e:
        print(f"❌ Error en endpoint de chat: {e}")
        return jsonify({
            "answer": "Lo siento, ocurrió un error procesando tu pregunta."
        }), 500


@chat_bp.route("/api/chat/history", methods=["GET"])
def get_history():
    """
    Obtiene el historial reciente de una sesión.

    Parámetros query:
      - session_id: id de sesión
      - limit: número máximo de turnos a retornar (por defecto 8)
    """
    try:
        session_id = request.args.get("session_id", type=str)
        limit = request.args.get("limit", default=8, type=int)
        if not session_id:
            return jsonify({"history": []})
        service = init_chat_service()
        turns = service.history_store.get_recent(session_id, limit=max(1, limit))
        return jsonify({
            "history": [
                {"role": t.role, "content": t.content, "timestamp": t.timestamp} for t in turns
            ]
        })
    except Exception as e:
        print(f"❌ Error obteniendo historial: {e}")
        return jsonify({"history": [], "error": str(e)}), 500


@chat_bp.route("/api/chat/clear-history", methods=["POST"])
def clear_history():
    """
    Limpia el historial de una sesión.
    Cuerpo JSON: { "session_id": "..." }
    """
    try:
        data = request.get_json(force=True) or {}
        session_id = data.get("session_id")
        if not session_id:
            return jsonify({"message": "session_id requerido"}), 400
        service = init_chat_service()
        removed = service.history_store.clear(session_id)
        return jsonify({"message": "Historial limpiado", "removed": removed})
    except Exception as e:
        print(f"❌ Error limpiando historial: {e}")
        return jsonify({"message": "Error limpiando historial", "error": str(e)}), 500


@chat_bp.route("/api/chat/health", methods=["GET"])
def health():
    """
    Endpoint para verificar el estado del servicio
    
    Retorna:
    {
        "status": "string",
        "details": {...}
    }
    """
    try:
        service = init_chat_service()
        
        is_healthy = service.health_check()
        status_details = service.get_service_status()
        
        return jsonify({
            "status": "healthy" if is_healthy else "unhealthy",
            "details": status_details
        })
        
    except Exception as e:
        print(f"❌ Error en health check: {e}")
        return jsonify({
            "status": "error",
            "details": {"error": str(e)}
        }), 500


@chat_bp.route("/api/chat/test-google-ai", methods=["GET"])
def test_google_ai():
    """
    Endpoint para probar la conexión con Google AI Studio
    
    Retorna:
    {
        "status": "string",
        "details": {...}
    }
    """
    try:
        service = init_chat_service()
        
        # Realizar prueba de conexión
        test_result = service.google_ai_client.test_connection()
        
        return jsonify({
            "status": "success" if test_result["success"] else "error",
            "message": test_result["message"],
            "details": test_result.get("details", {}),
            "test_response": test_result.get("test_response", "")
        })
        
    except Exception as e:
        print(f"❌ Error en test de Google AI: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error en prueba de conexión: {str(e)}"
        }), 500


@chat_bp.route("/api/chat/reload", methods=["POST"])
def reload_documents():
    """
    Endpoint para recargar los documentos
    
    Retorna:
    {
        "message": "string",
        "documents_loaded": int
    }
    """
    try:
        service = init_chat_service()
        
        documents_count = service.reload_documents()
        
        return jsonify({
            "message": "Documentos recargados exitosamente",
            "documents_loaded": documents_count
        })
        
    except Exception as e:
        print(f"❌ Error recargando documentos: {e}")
        return jsonify({
            "message": "Error recargando documentos",
            "error": str(e)
        }), 500


@chat_bp.route("/api/chat/analyze-image", methods=["POST"])
def chat_analyze_image():
    """
    Endpoint para analizar imágenes culturales con chat integrado
    
    Acepta form-data con:
    - file: archivo de imagen
    - question: pregunta opcional sobre la imagen
    - session_id: opcional para historial
    
    Retorna:
    {
        "analysis": {...},
        "cultural_context": "string",
        "chat_response": "string?",
        "combined_analysis": "string"
    }
    """
    try:
        # Verificar que hay un archivo
        if 'file' not in request.files:
            return jsonify({"error": "No se encontró ningún archivo"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No se seleccionó ningún archivo"}), 400
        
        # Obtener parámetros opcionales
        user_question = request.form.get('question', '').strip()
        session_id = request.form.get('session_id', '').strip()
        
        # Validar que es una imagen
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        file_ext = '.' + file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_ext not in allowed_extensions:
            return jsonify({
                "error": f"Tipo de archivo no soportado. Use: {', '.join(allowed_extensions)}"
            }), 400
        
        # Guardar archivo temporalmente
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            file.save(tmp_file.name)
            temp_path = tmp_file.name
        
        try:
            # Inicializar servicio de chat
            service = init_chat_service()
            
            # Analizar imagen
            result = service.analyze_cultural_image(temp_path, user_question)
            
            # Agregar al historial si hay session_id y chat_response
            if session_id and result.get('chat_response'):
                try:
                    question_for_history = f"[Imagen: {file.filename}]"
                    if user_question:
                        question_for_history += f" {user_question}"
                    
                    service.history_store.append(session_id, "user", question_for_history)
                    service.history_store.append(session_id, "assistant", result['chat_response'])
                except Exception as e:
                    print(f"⚠️ Error guardando en historial: {e}")
            
            return jsonify(result)
            
        finally:
            # Limpiar archivo temporal
            try:
                os.unlink(temp_path)
            except:
                pass
        
    except Exception as e:
        print(f"❌ Error en análisis de imagen: {e}")
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


def register_chat_routes(app):
    """
    Registra las rutas de chat en la aplicación Flask
    
    Args:
        app: Instancia de la aplicación Flask
    """
    app.register_blueprint(chat_bp)
    print("✅ Rutas de chat registradas")