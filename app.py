"""
Aplicación principal del chatbot ORIGEN
Archivo simplificado que solo configura e inicia la aplicación
"""
from flask import Flask
from config import SERVER_HOST, SERVER_PORT, DEBUG_MODE
from routes.chat_routes import register_chat_routes
from routes.aluna_routes import register_origen_routes
from routes.conversation_routes import register_conversation_routes

# Importar módulos de funcionalidades adicionales
from routes.upload_routes import register_upload_routes
from routes.vision_routes import vision_bp
from scripts.reset_embeddings import registrar_ruta_reset


def create_app() -> Flask:
    """
    Factory function para crear la aplicación Flask
    
    Returns:
        Instancia configurada de Flask
    """
    app = Flask(__name__)
    
    # Registrar rutas principales de chat
    register_chat_routes(app)
    register_origen_routes(app)
    register_conversation_routes(app)
    
    # Registrar rutas adicionales de otros módulos
    register_upload_routes(app)
    registrar_ruta_reset(app)
    
    # Registrar blueprint de visión computacional
    app.register_blueprint(vision_bp)
    
    print("🚀 Aplicación ORIGEN configurada exitosamente")
    return app


def main():
    """Función principal para iniciar la aplicación"""
    print("=" * 50)
    print("🦎 Iniciando ORIGEN - Memoria de la Sierra")
    print("=" * 50)
    
    # Crear aplicación
    app = create_app()
    
    # Iniciar servidor
    print(f"🌐 Servidor iniciando en http://{SERVER_HOST}:{SERVER_PORT}")
    print(f"🐛 Modo debug: {DEBUG_MODE}")
    print("=" * 50)
    
    app.run(
        host=SERVER_HOST,
        port=SERVER_PORT,
        debug=DEBUG_MODE
    )


if __name__ == "__main__":
    main()
     