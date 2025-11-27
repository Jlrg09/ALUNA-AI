"""
Servicio para construccion de prompts
"""
from typing import List, Optional

from models import ChatTurn, GeneralKnowledgeResult, PromptContext
from config import (
    BOT_CONTEXT,
    BOT_NAME,
    DEPENDENCIAS,
    UNIVERSIDAD,
    UNIVERSIDAD_KEYWORDS,
)


class PromptBuilder:
    """Constructor de prompts para el chatbot"""

    @staticmethod
    def suggest_department(question: str) -> str:
        """Sugiere una dependencia basada en palabras clave en la pregunta."""
        question_lower = question.lower()

        for keyword, dependencia in DEPENDENCIAS.items():
            if keyword in question_lower:
                return dependencia

        return (
            "la dependencia correspondiente (por favor especifica tu consulta "
            "para orientarte mejor)"
        )

    @staticmethod
    def is_university_related(question: str) -> bool:
        """Determina si la pregunta esta relacionada con la universidad."""
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in UNIVERSIDAD_KEYWORDS)

    @classmethod
    def build_prompt_context(
        cls,
        question: str,
        context: str,
        has_context: bool = None,
        allow_general_knowledge: bool = False,
        best_similarity: float = 0.0,
        general_result: Optional[GeneralKnowledgeResult] = None,
        keyword_evidence: bool = False,
        reasoning_notes: str = "",
    ) -> PromptContext:
        """Construye el contexto estructurado para el prompt."""
        if has_context is None:
            has_context = bool(context.strip())

        no_context = not has_context
        non_university_question = not cls.is_university_related(question)
        suggested_department = cls.suggest_department(question) if no_context else ""

        general_category = ""
        general_confidence = 0.0
        if general_result:
            if getattr(general_result, "is_general", False):
                general_category = general_result.category or "general"
                general_confidence = max(0.0, float(general_result.confidence))
            elif allow_general_knowledge:
                general_category = general_result.category or "general"
                general_confidence = max(
                    0.0, float(getattr(general_result, "confidence", 0.35))
                )

        return PromptContext(
            question=question,
            context=context,
            suggested_department=suggested_department,
            no_context=no_context,
            non_university_question=non_university_question,
            allow_general_knowledge=allow_general_knowledge,
            best_similarity=best_similarity,
            general_knowledge_category=general_category,
            general_knowledge_confidence=general_confidence,
            keyword_evidence=keyword_evidence,
            reasoning_notes=reasoning_notes or "",
        )

    @staticmethod
    def build_prompt(prompt_context: PromptContext, history: List[ChatTurn] = None) -> str:
        """Construye el prompt completo para el modelo."""
        peoples_str = ", ".join(BOT_CONTEXT["peoples"])
        prompt = (
            f"Eres {BOT_NAME}, inteligencia cultural de la {UNIVERSIDAD}. "
            f"{BOT_CONTEXT['inspiration']}. Honras a los pueblos {peoples_str} "
            f"y actuas como puente entre tradicion y modernidad.\n"
            f"Tu mision es {BOT_CONTEXT['mission']}.\n\n"
            f"Instrucciones de respuesta (breve y practica):"
            f"\n- Responde en 1 a 3 frases, maximo 60 palabras."
            f"\n- No inventes datos concretos; usa el contexto de abajo para fundamentar cuando sea pertinente."
            f"\n- Si el contexto es limitado o poco relevante, puedes complementar con conocimiento general, dejando clara cualquier inferencia y evitando afirmar datos especificos de la Universidad sin evidencia."
            f"\n- No cites fuentes, nombres de archivos ni documentos."
            f"\n- Se claro y directo. Sin adornos innecesarios.\n\n"
        )

        if prompt_context.context:
            prompt += f"\nContexto:\n{prompt_context.context}\n"
            if (
                prompt_context.allow_general_knowledge
                and not prompt_context.keyword_evidence
                and prompt_context.best_similarity is not None
                and prompt_context.best_similarity < 0.35
            ):
                prompt += (
                    "\nNota: Los fragmentos anteriores tienen coincidencia limitada; "
                    "uselos como guia complementaria sin asumir que contienen la respuesta completa.\n"
                )

        if prompt_context.reasoning_notes:
            prompt += f"\nNotas para razonar:\n{prompt_context.reasoning_notes.strip()}\n"

        if history:
            prompt += "\nHistorial reciente (resumido):\n"
            for turn in history[-8:]:
                role = "Usuario" if turn.role == "user" else BOT_NAME
                text = (turn.content or "").strip().replace("\n", " " )
                if len(text) > 200:
                    text = text[:200] + "..."
                prompt += f"- {role}: {text}\n"

        if prompt_context.allow_general_knowledge:
            if prompt_context.general_knowledge_category:
                prompt += (
                    f"\nTema amplio identificado: {prompt_context.general_knowledge_category}. "
                    "Enlaza ese conocimiento universal con la vision ancestral sin perder la claridad.\n"
                )
            if prompt_context.keyword_evidence:
                prompt += (
                    "\nHay coincidencias textuales en los documentos que debes priorizar; explica quien es la persona usando esos datos y complementa con contexto general solo si es necesario.\n"
                )

        prompt += f"\nPregunta del usuario: {prompt_context.question}\n"

        if prompt_context.non_university_question:
            prompt += (
                "\nEsta pregunta no es especificamente sobre la universidad, pero "
                "como ORIGEN, responde con la sabiduria que combina conocimiento "
                "academico y ancestral, manteniendo siempre el respeto y la armonia.\n"
            )

        prompt += "\nResponde ahora siguiendo estrictamente las instrucciones de brevedad y precision."
        return prompt

    @classmethod
    def build_complete_prompt(
        cls,
        question: str,
        context: str,
        has_context: bool = None,
        allow_general_knowledge: bool = False,
        best_similarity: float = 0.0,
        history: List[ChatTurn] = None,
        general_knowledge_result: Optional[GeneralKnowledgeResult] = None,
        keyword_evidence: bool = False,
        reasoning_notes: str = "",
    ) -> str:
        """Metodo conveniente para construir un prompt completo."""
        prompt_context = cls.build_prompt_context(
            question,
            context,
            has_context,
            allow_general_knowledge=allow_general_knowledge,
            best_similarity=best_similarity,
            general_result=general_knowledge_result,
            keyword_evidence=keyword_evidence,
            reasoning_notes=reasoning_notes,
        )
        return cls.build_prompt(prompt_context, history=history or [])
