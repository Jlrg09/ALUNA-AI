"""
Rutas API para gestión de conversaciones
"""
from flask import Blueprint, request, jsonify
from services.conversation_manager import ConversationManager

# Crear blueprint para las rutas de conversaciones
conversations_bp = Blueprint('conversations', __name__, url_prefix='/api/conversations')

# Instancia del gestor de conversaciones
conversation_manager = ConversationManager()

@conversations_bp.route('/', methods=['GET'])
def get_conversations():
    """
    Obtiene todas las conversaciones
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        conversations = conversation_manager.get_all_conversations(limit=limit)
        
        return jsonify({
            "success": True,
            "conversations": conversations
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@conversations_bp.route('/', methods=['POST'])
def create_conversation():
    """
    Crea una nueva conversación
    """
    try:
        conversation = conversation_manager.create_conversation()
        
        return jsonify({
            "success": True,
            "conversation": conversation
        }), 201
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@conversations_bp.route('/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """
    Obtiene una conversación específica
    """
    try:
        conversation = conversation_manager.get_conversation(conversation_id)
        
        if conversation:
            return jsonify({
                "success": True,
                "conversation": conversation
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Conversación no encontrada"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@conversations_bp.route('/<conversation_id>/messages', methods=['POST'])
def add_message(conversation_id):
    """
    Agrega un mensaje a una conversación
    """
    try:
        data = request.get_json()
        message_type = data.get('type')
        content = data.get('content')
        
        if not message_type or not content:
            return jsonify({
                "success": False,
                "error": "Tipo y contenido del mensaje son requeridos"
            }), 400
        
        success = conversation_manager.add_message(conversation_id, message_type, content)
        
        if success:
            # Obtener la conversación actualizada
            conversation = conversation_manager.get_conversation(conversation_id)
            return jsonify({
                "success": True,
                "conversation": conversation
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "No se pudo agregar el mensaje"
            }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@conversations_bp.route('/<conversation_id>/title', methods=['PUT'])
def update_title(conversation_id):
    """
    Actualiza el título de una conversación
    """
    try:
        data = request.get_json()
        title = data.get('title')
        
        if not title:
            return jsonify({
                "success": False,
                "error": "Título es requerido"
            }), 400
        
        success = conversation_manager.update_title(conversation_id, title)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Título actualizado correctamente"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "No se pudo actualizar el título"
            }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@conversations_bp.route('/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """
    Elimina una conversación
    """
    try:
        success = conversation_manager.delete_conversation(conversation_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Conversación eliminada correctamente"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "No se pudo eliminar la conversación"
            }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@conversations_bp.route('/<conversation_id>/clear', methods=['POST'])
def clear_conversation(conversation_id):
    """
    Limpia los mensajes de una conversación sin eliminarla
    """
    try:
        success = conversation_manager.clear_conversation(conversation_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Conversación limpiada correctamente"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "No se pudo limpiar la conversación"
            }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def register_conversation_routes(app):
    """
    Registra las rutas de conversaciones en la aplicación Flask
    
    Args:
        app: Instancia de la aplicación Flask
    """
    app.register_blueprint(conversations_bp)
    print("✅ Rutas de conversaciones registradas")
