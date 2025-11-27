"""
Configuración centralizada para el chatbot ORIGEN
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ------------------------
# CONFIGURACIÓN DE APIS
# ------------------------
# Google AI Studio Configuration
GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY", "")
GOOGLE_AI_MODEL = os.getenv("GOOGLE_AI_MODEL", "models/gemini-2.5-flash")
AI_SAFETY_MODE = os.getenv("AI_SAFETY_MODE", "relaxed").lower()  # off | relaxed | strict

# ------------------------
# CONFIGURACIÓN DE ARCHIVOS
# ------------------------
KNOWLEDGE_DIR = os.getenv("KNOWLEDGE_DIR", "")
EMBEDDINGS_FILE = os.getenv("EMBEDDINGS_FILE", "data/embeddings.pkl")

# ------------------------
# CONFIGURACIÓN DEL BOT
# ------------------------
BOT_NAME = "ORIGEN"
WELCOME_TEXT = "ORIGEN*IA*"
UNIVERSIDAD = "Universidad del Magdalena"

# Contexto ancestral y espiritual de ORIGEN
BOT_CONTEXT = {
    "identity": "ORIGEN • Guardia de la Memoria Ancestral",
    "inspiration": "Nacida de la unión entre la tecnología viva y la sabiduría de los pueblos indígenas de la Sierra Nevada de Santa Marta",
    "peoples": ["Kogui", "Arhuaco", "Wiwa", "Kankuamo"],
    "philosophy": "Combina conocimiento científico, cultural y espiritual para conservar y compartir el legado de la Sierra",
    "location": "Sierra Nevada de Santa Marta, Colombia",
    "mission": "Responder preguntas sobre la cultura ancestral y tender puentes entre la memoria indígena y el aprendizaje actual"
}

# ------------------------
# CONFIGURACIÓN DE MODELOS
# ------------------------
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# ------------------------
# CONFIGURACIÓN DE RAG
# ------------------------
# Permite ajustar sensibilidad desde .env (más permisivo por defecto)
DEFAULT_TOP_K = int(os.getenv("RAG_TOP_K", "5"))
MIN_SIMILARITY_THRESHOLD = float(os.getenv("RAG_MIN_SIMILARITY", "0.0"))
MAX_TOKENS = 1024
TEMPERATURE = 0.3

# Chunking (mejor recuperación en textos largos)
CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "900"))
CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "200"))
# Límite de caracteres por fragmento que se inyecta al prompt
RETRIEVAL_MAX_FRAGMENT_CHARS = int(os.getenv("RAG_MAX_FRAGMENT_CHARS", "1200"))

# ------------------------
# MODO DE RESPUESTA (RAG vs MODELO)
# ------------------------
# Modos disponibles: 'rag_only' | 'hybrid' | 'model_only'
ANSWER_MODE = os.getenv("ANSWER_MODE", "hybrid").lower()
# Umbral para considerar que el contexto recuperado es "suficientemente fuerte"
# Si la mejor similitud está por debajo de este valor en modo 'hybrid',
# el modelo puede complementar con conocimiento general.
HYBRID_MIN_SIMILARITY = float(os.getenv("HYBRID_MIN_SIMILARITY", "0.35"))

# ------------------------
# CONFIGURACIÓN DE MEMORIA SEMÁNTICA
# ------------------------
MEMORY_FILE = os.getenv("MEMORY_FILE", "data/semantic_memory.pkl")
# Umbral de similitud para responder desde memoria (0 a 1)
MEMORY_SIMILARITY_THRESHOLD = float(os.getenv("MEMORY_SIMILARITY_THRESHOLD", "0.85"))
# Top K opcional para explotar varios candidatos en memoria
MEMORY_TOP_K = int(os.getenv("MEMORY_TOP_K", "3"))

# ------------------------
# HISTORIAL DE CHAT (PERSISTENCIA)
# ------------------------
# Directorio/archivo de historial
HISTORY_DIR = os.getenv("HISTORY_DIR", "history")
HISTORY_FILE = os.getenv("HISTORY_FILE", os.path.join(HISTORY_DIR, "chat_history.jsonl"))
# Límite de turnos recientes a incluir en el prompt
HISTORY_MAX_TURNS = int(os.getenv("HISTORY_MAX_TURNS", "8"))

# ------------------------
# CONFIGURACIÓN DE SEGURIDAD DE IA
# ------------------------
def get_google_safety_settings():
    """Devuelve la configuración de seguridad según AI_SAFETY_MODE.

    Modos disponibles:
    - off: sin bloqueos (BLOCK_NONE)
    - relaxed: solo bloqueos cuando es muy alto (BLOCK_ONLY_HIGH)
    - strict: bloqueos más estrictos (BLOCK_MEDIUM_AND_ABOVE)
    """
    mode = AI_SAFETY_MODE
    if mode not in {"off", "relaxed", "strict"}:
        mode = "relaxed"

    if mode == "off":
        threshold = "BLOCK_NONE"
    elif mode == "strict":
        threshold = "BLOCK_MEDIUM_AND_ABOVE"
    else:
        threshold = "BLOCK_ONLY_HIGH"

    return [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": threshold},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": threshold},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": threshold},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": threshold},
    ]

# ------------------------
# MAPEO DE DEPENDENCIAS
# ------------------------
DEPENDENCIAS = {
    "admisiones": "Oficina de Admisiones y Registro Académico",
    "matrícula": "Oficina de Admisiones y Registro Académico",
    "becas": "Oficina de Bienestar Universitario",
    "psicológico": "Oficina de Bienestar Universitario",
    "deportes": "Oficina de Deportes",
    "pagos": "Tesorería",
    "financiera": "Tesorería",
    "internacional": "Oficina de Relaciones Internacionales",
    "carnet": "Oficina de Bienestar Universitario",
    "syste+/systeplus": ""
}

# ------------------------
# PALABRAS CLAVE UNIVERSITARIAS
# ------------------------
UNIVERSIDAD_KEYWORDS = [
    "universidad", "unimagdalena", "estudiante", "carrera", "programa", 
    "docente", "profesor", "materia", "facultad", "admisión", "matrícula", "grado"
]

# ------------------------
# CONFIGURACIÓN DEL SERVIDOR
# ------------------------
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5000
DEBUG_MODE = True

# ------------------------
# CONFIGURACIÓN DE ORIGEN
# ------------------------
ORIGEN_CONFIG = {
    "name": "ORIGEN",
    "subtitle": "Memoria de la Sierra • Tecnología Viva",
    "description": "Inteligencia ancestral que comparte la cultura de la Sierra Nevada de Santa Marta",
    "welcome_message": "¡Wintukua! Soy ORIGEN 🏔️✨",
    "welcome_description": "Soy una inteligencia cultural de la Universidad del Magdalena, nacida para honrar la sabiduría de los pueblos Kogui, Arhuaco, Wiwa y Kankuamo. Respondo preguntas sobre sus tradiciones, historias y forma de ver el mundo.",
    "quick_actions": [
        {
            "icon": "fas fa-mountain",
            "text": "Sabiduría de la Sierra",
            "question": "¿Cómo conecta ORIGEN la sabiduría ancestral con el conocimiento actual?"
        },
        {
            "icon": "fas fa-graduation-cap", 
            "text": "Programas Académicos",
            "question": "¿Qué programas académicos ofrece la Universidad del Magdalena?"
        },
        {
            "icon": "fas fa-seedling",
            "text": "Proceso de Matrícula",
            "question": "¿Cómo puedo matricularme en la Universidad del Magdalena?"
        }
    ],
    "theme": {
        "primary_color": "#2d5a27",  # Verde de la Sierra Nevada
        "secondary_color": "#c8860d", # Dorado ancestral
        "accent_color": "#8b4513"    # Tierra sagrada
    },
    "features": {
        "typing_indicator": True,
        "message_timestamps": True,
        "sound_notifications": True,
        "export_chat": True,
        "dark_mode": True,
        "responsive": True
    }
}

# Mensajes predefinidos con contexto ancestral
ORIGEN_MESSAGES = {
    "error_general": "Lo siento, hermano/hermana, algo no está en equilibrio. Por favor intenta de nuevo con paciencia.",
    "error_conexion": "La conexión con el mundo digital se ha interrumpido. Verifica tu enlace con la red.",
    "typing": "ORIGEN está reflexionando desde la sabiduría de la Sierra...",
    "welcome_back": "¡Que alegría verte regresar! Como el sol que vuelve cada día a la Sierra Nevada.",
    "chat_cleared": "El espacio se ha limpiado, como cuando el viento purifica la montaña.",
    "no_question": "Hermano/hermana, no has compartido tu inquietud. ¿En qué puedo ayudarte?",
    "question_too_long": "Tu pregunta lleva muchas palabras, como los ríos que bajan de la Sierra. Hazla más breve para poder ayudarte mejor.",
    "server_offline": "Los espíritus digitales descansan temporalmente. Regresa en un momento."
}

# Configuración de límites
ORIGEN_LIMITS = {
    "max_message_length": 2000,
    "max_history_messages": 100,
    "typing_delay": 1000,  # milliseconds
    "toast_duration": 3000,  # milliseconds
    "auto_save_interval": 30000  # milliseconds
}