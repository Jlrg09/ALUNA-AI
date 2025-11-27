"""
Configuración simplificada sin dependencias externas problemáticas
"""
import os

# Configuración básica
BOT_NAME = "ORIGEN"
UNIVERSIDAD = "Universidad del Magdalena"

# Directorios
KNOWLEDGE_DIR = "documentos"
EMBEDDINGS_FILE = "embeddings_simple.json"

# Configuración de ORIGEN simplificada
ORIGEN_CONFIG = {
    "name": "ORIGEN",
    "subtitle": "Memoria de la Sierra • Tecnología Viva",
    "description": "Inteligencia ancestral que comparte la cultura de la Sierra Nevada",
    "welcome_message": "¡Wintukua! Soy ORIGEN 🏔️✨",
    "welcome_description": "Soy una inteligencia artificial de la Universidad del Magdalena, inspirada en la sabiduría ancestral de los pueblos indígenas de la Sierra Nevada de Santa Marta.",
    "quick_actions": [
        {
            "icon": "fas fa-mountain",
            "text": "Sobre ORIGEN",
            "question": "¿Qué es ORIGEN?"
        },
        {
            "icon": "fas fa-graduation-cap", 
            "text": "Programas",
            "question": "¿Qué programas ofrece la Universidad?"
        },
        {
            "icon": "fas fa-info-circle",
            "text": "Información",
            "question": "¿Cómo puedo obtener más información?"
        }
    ]
}

# Mensajes del sistema
SYSTEM_MESSAGES = {
    "error_general": "Lo siento, algo no está funcionando correctamente. Por favor intenta de nuevo.",
    "error_conexion": "Hay un problema de conexión. Verifica tu red.",
    "no_question": "No has hecho ninguna pregunta. ¿En qué puedo ayudarte?",
    "processing": "Procesando tu consulta...",
    "success": "Consulta procesada exitosamente."
}

# Configuración del servidor
SERVER_CONFIG = {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": True
}

# Palabras clave universitarias
UNIVERSITY_KEYWORDS = [
    "universidad", "unimagdalena", "estudiante", "carrera", "programa", 
    "docente", "profesor", "materia", "facultad", "admision", "matricula", 
    "grado", "pregrado", "posgrado", "maestria", "doctorado"
]

def get_knowledge_dir():
    """Obtiene el directorio de conocimiento, creándolo si no existe"""
    if not os.path.exists(KNOWLEDGE_DIR):
        os.makedirs(KNOWLEDGE_DIR, exist_ok=True)
    return KNOWLEDGE_DIR

def is_university_question(text: str) -> bool:
    """Verifica si una pregunta está relacionada con la universidad"""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in UNIVERSITY_KEYWORDS)
