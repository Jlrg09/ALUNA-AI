"""
Rutas para la interfaz web de ORIGEN
"""
from flask import Blueprint, render_template, jsonify
from config import ORIGEN_CONFIG, ORIGEN_MESSAGES, ORIGEN_LIMITS

# Crear blueprint para las rutas de la interfaz
origen_bp = Blueprint('origen', __name__)

@origen_bp.route("/")
@origen_bp.route("/origen")
@origen_bp.route("/aluna")
def index():
    """
    Página principal de ORIGEN
    Renderiza la interfaz de chat cultural
    """
    return render_template('aluna_chat.html', 
                         config=ORIGEN_CONFIG,
                         messages=ORIGEN_MESSAGES,
                         limits=ORIGEN_LIMITS)

@origen_bp.route("/chat")
def chat_interface():
    """
    Ruta de compatibilidad para la interfaz de chat
    """
    return render_template('aluna_chat.html',
                         config=ORIGEN_CONFIG,
                         messages=ORIGEN_MESSAGES,
                         limits=ORIGEN_LIMITS)

@origen_bp.route("/api/origen/config")
@origen_bp.route("/api/aluna/config")
def get_origen_config():
    """
    API endpoint para obtener la configuración de ORIGEN
    """
    return jsonify({
        "config": ORIGEN_CONFIG,
        "messages": ORIGEN_MESSAGES,
        "limits": ORIGEN_LIMITS
    })

def register_origen_routes(app):
    """
    Registra las rutas de ORIGEN en la aplicación Flask
    
    Args:
        app: Instancia de la aplicación Flask
    """
    app.register_blueprint(origen_bp)
    print("✅ Rutas de ORIGEN registradas")