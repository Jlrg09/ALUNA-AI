"""Módulo heurístico para clasificar preguntas de conocimiento general."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
import re

from config import UNIVERSIDAD_KEYWORDS
from models import GeneralKnowledgeResult


@dataclass
class _CategorySignals:
    """Estructura interna para acumular señales"""
    category: str
    weight: float
    matches: List[str]


class GeneralKnowledgeEngine:
    """Clasificador simple para determinar si una pregunta requiere conocimiento general."""

    # Prefijos típicos en preguntas abiertas de cultura general
    GENERAL_PREFIXES = (
        "¿qué es",
        "que es",
        "¿quién es",
        "quien es",
        "¿quién fue",
        "quien fue",
        "¿cuál es",
        "cual es",
        "¿cómo funciona",
        "como funciona",
        "¿por qué",
        "por que",
        "what is",
        "who is",
        "how does",
        "why is",
        "tell me about",
    )

    # Categorías de alto nivel con palabras clave asociadas
    CATEGORY_KEYWORDS: Dict[str, tuple[str, ...]] = {
        "ciencia": (
            "átomo", "atomo", "física", "fisica", "biología", "biologia",
            "química", "quimica", "universo", "planeta", "ciencia", "energía",
            "energia", "teoría", "teoria", "gravedad", "evolución", "evolucion",
        ),
        "historia": (
            "historia", "revolución", "revolucion", "guerra", "imperio", "presidente",
            "rey", "reina", "civilización", "civilizacion", "siglo", "batalla",
        ),
        "tecnología": (
            "tecnología", "tecnologia", "programación", "programacion", "software",
            "internet", "inteligencia artificial", "algoritmo", "computadora",
            "smartphone", "robot", "criptomoneda",
        ),
        "cultura": (
            "literatura", "mitología", "mitologia", "arte", "música", "musica",
            "película", "pelicula", "actor", "celebridad", "religión", "religion",
        ),
        "deportes": (
            "fútbol", "futbol", "baloncesto", "nba", "mundial", "olímpico",
            "olimpico", "tenis", "selección", "seleccion", "deporte",
        ),
    }

    GENERAL_CONNECTORS = (
        "explica", "describe", "resumen", "cuéntame", "cuentame", "dame datos",
        "información", "informacion", "detalles", "concepto",
    )

    SIMILARITY_LOW_THRESHOLD = 0.32
    BASE_ACTIVATION = 1.2

    def __init__(self) -> None:
        self._university_keywords = tuple(kw.lower() for kw in UNIVERSIDAD_KEYWORDS)

    def _contains_university_term(self, question_lower: str) -> bool:
        return any(keyword in question_lower for keyword in self._university_keywords)

    def _collect_category_signal(self, question_lower: str) -> _CategorySignals | None:
        best_signal = None
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            matches = [kw for kw in keywords if kw in question_lower]
            if matches:
                weight = 0.8 + 0.15 * min(len(matches), 3)
                if not best_signal or weight > best_signal.weight:
                    best_signal = _CategorySignals(category=category, weight=weight, matches=matches)
        return best_signal

    def classify(self, question: str, *, best_similarity: float = 0.0, has_context: bool = False) -> GeneralKnowledgeResult:
        """Evalúa la pregunta y determina si requiere conocimiento general.

        Args:
            question: Texto original del usuario.
            best_similarity: Mejor similitud encontrada con documentos propios.
            has_context: Indica si se encontró contexto significativo.

        Returns:
            GeneralKnowledgeResult con la decisión heurística.
        """
        if not question:
            return GeneralKnowledgeResult(is_general=False, reason="pregunta vacía")

        normalized = re.sub(r"\s+", " ", question.strip().lower())

        if self._contains_university_term(normalized):
            return GeneralKnowledgeResult(is_general=False, reason="coincidencias con palabra clave institucional")

        score = 0.0
        reasons: List[str] = []
        category_signal = self._collect_category_signal(normalized)

        if category_signal:
            score += category_signal.weight
            reasons.append(f"palabras clave de {category_signal.category}: {', '.join(category_signal.matches[:3])}")

        if any(prefix in normalized for prefix in self.GENERAL_PREFIXES):
            score += 0.8
            reasons.append("prefijo interrogativo general")

        if any(connector in normalized for connector in self.GENERAL_CONNECTORS):
            score += 0.4
            reasons.append("solicitud de explicación")

        if not has_context or best_similarity < self.SIMILARITY_LOW_THRESHOLD:
            score += 0.5
            reasons.append("sin contexto relevante")

        if len(normalized.split()) >= 5:
            score += 0.2

        is_general = score >= self.BASE_ACTIVATION
        confidence = max(0.0, min(1.0, score / 3.0))
        category = category_signal.category if category_signal else "general"
        reason_text = "; ".join(reasons) if reasons else "sin señales fuertes"

        return GeneralKnowledgeResult(
            is_general=is_general,
            category=category if is_general else "",
            confidence=confidence if is_general else 0.0,
            reason=reason_text,
        )
