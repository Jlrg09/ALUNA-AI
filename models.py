"""
Modelos y tipos de datos para el chatbot IguiChat
"""
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, field
import numpy as np
from time import time

# ------------------------
# TIPOS BÁSICOS
# ------------------------
DocumentTuple = Tuple[str, str]  # (filename, content)
EmbeddingArray = np.ndarray

# ------------------------
# DATACLASSES
# ------------------------
@dataclass
class Document:
    """Representa un documento con su nombre y contenido"""
    filename: str
    content: str
    
    def to_tuple(self) -> DocumentTuple:
        """Convierte el documento a tupla para compatibilidad"""
        return (self.filename, self.content)

@dataclass
class EmbeddingData:
    """Estructura para almacenar datos de embeddings"""
    embeddings: EmbeddingArray
    filenames: List[str]
    texts: List[str]
    meta: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para serialización"""
        return {
            "embeddings": self.embeddings,
            "filenames": self.filenames,
            "texts": self.texts,
            "meta": self.meta,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmbeddingData':
        """Crea instancia desde diccionario"""
        return cls(
            embeddings=data["embeddings"],
            filenames=data["filenames"],
            texts=data["texts"],
            meta=data.get("meta", {}),
        )

@dataclass
class SearchResult:
    """Resultado de búsqueda de contexto"""
    context: str
    similarity_scores: List[float]
    relevant_indices: List[int]
    has_relevant_content: bool
    # Mejor similitud encontrada para la pregunta (0..1). Útil para decisiones híbridas.
    best_similarity: float = 0.0

@dataclass
class ChatRequest:
    """Solicitud de chat del usuario"""
    question: str
    # Identificador de sesión para historial/persistencia
    session_id: Optional[str] = None
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'ChatRequest':
        """Crea instancia desde JSON"""
        return cls(
            question=data.get("question", "").strip(),
            session_id=(data.get("session_id") or None)
        )

@dataclass
class ChatResponse:
    """Respuesta del chatbot"""
    answer: str

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para JSON"""
        return {"answer": self.answer}


@dataclass
class GeneralKnowledgeResult:
    """Resultado del clasificador de conocimiento general"""
    is_general: bool
    category: str = ""
    confidence: float = 0.0
    reason: str = ""


@dataclass
class PromptContext:
    """Contexto para construcción de prompts"""
    question: str
    context: str
    suggested_department: str
    no_context: bool
    non_university_question: bool
    # Extensiones para modo híbrido
    allow_general_knowledge: bool = False
    best_similarity: float = 0.0
    general_knowledge_category: str = ""
    general_knowledge_confidence: float = 0.0
    keyword_evidence: bool = False
    reasoning_notes: str = ""


@dataclass
class SafetyProtocolResult:
    """Resultado de la evaluación de protocolos de seguridad."""
    triggered: bool
    severity: str = ""
    message: str = ""
    matched_terms: List[str] = field(default_factory=list)
    label: str = ""
    recommendations: List[str] = field(default_factory=list)
    alert_required: bool = False


@dataclass
class ChatTurn:
    """Turno de conversación para historial"""
    role: str  # "user" | "assistant"
    content: str
    timestamp: float = field(default_factory=time)


@dataclass
class OpenRouterRequest:
    """Estructura para solicitudes a OpenRouter"""
    model: str
    messages: List[Dict[str, str]]
    max_tokens: int
    temperature: float

# ------------------------
# MEMORIA SEMÁNTICA (Q/A CACHE)
# ------------------------
@dataclass
class MemoryEntry:
    """Entrada de memoria semántica para cachear preguntas/respuestas.

    Campos:
    - question: texto de la pregunta
    - answer: respuesta generada
    - embedding: vector de la pregunta (np.ndarray de forma (D,))
    - created_at: timestamp de creación (segundos)
    - last_used_at: último uso (segundos)
    - usage_count: número de veces que fue reutilizada
    - last_score: última similitud usada para hit
    """
    question: str
    answer: str
    embedding: EmbeddingArray
    created_at: float = time()
    last_used_at: float = time()
    usage_count: int = 0
    last_score: float = 0.0