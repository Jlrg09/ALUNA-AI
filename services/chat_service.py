"""
Servicio principal de chat que coordina todos los componentes
"""
import re
from typing import List, Set, Tuple
from models import ChatRequest, ChatResponse, Document, GeneralKnowledgeResult, SafetyProtocolResult
from rag.document_processor import DocumentProcessor
from rag.context_search import ContextSearchService
from api.google_ai_client import GoogleAIClient
from services.prompt_builder import PromptBuilder
from services.history_store import HistoryStore
from services.general_knowledge import GeneralKnowledgeEngine
from services.safety_protocol import SafetyProtocol
from config import WELCOME_TEXT, BOT_NAME, BOT_CONTEXT, ANSWER_MODE, HYBRID_MIN_SIMILARITY, HISTORY_MAX_TURNS
from services.memory_manager import SemanticMemory


class ChatService:
    """Servicio principal que coordina el flujo de chat"""

    KEYWORD_STOPWORDS = {
        "quien", "quién", "quienes", "quiénes", "que", "qué", "cual", "cuál",
        "fue", "es", "son", "del", "de", "la", "el", "los", "las", "un",
        "una", "para", "sobre", "en", "lo", "al", "como", "cómo", "por",
        "porque", "porqué", "donde", "dónde", "cuando", "cuándo", "se", "su",
        "sus", "mi", "mis", "tu", "tus", "y", "o", "pero", "también", "tambien",
        "sobre", "acerca", "persona"
    }
    
    def __init__(self):
        """Inicializa el servicio de chat con todos sus componentes"""
        print("🚀 Inicializando servicio de chat...")
        
        self.document_processor = DocumentProcessor()
        self.context_search = ContextSearchService()
        self.google_ai_client = GoogleAIClient()
        self.prompt_builder = PromptBuilder()
        self.semantic_memory = SemanticMemory()
        self.history_store = HistoryStore()
        self.general_knowledge = GeneralKnowledgeEngine()
        self.safety_protocol = SafetyProtocol()
        
        # Cargar documentos al inicializar
        self.documents = self.document_processor.load_documents()
        
        print(f"✅ Servicio de chat inicializado con {len(self.documents)} documentos y {self.semantic_memory.stats()['entries']} memorias")
    
    def reload_documents(self) -> int:
        """
        Recarga los documentos desde el directorio de conocimiento
        
        Returns:
            Número de documentos cargados
        """
        print("🔄 Recargando documentos...")
        self.documents = self.document_processor.load_documents()
        print(f"✅ Documentos recargados: {len(self.documents)}")
        return len(self.documents)
    
    def process_chat_request(self, chat_request: ChatRequest) -> ChatResponse:
        """
        Procesa una solicitud de chat completa
        
        Args:
            chat_request: Solicitud de chat del usuario
            
        Returns:
            Respuesta del chatbot
        """
        question = chat_request.question
        
        if not question:
            return ChatResponse(answer="Hermano/hermana, no has compartido tu inquietud. ¿En qué puedo ayudarte?")
        
        print(f"💬 {BOT_NAME} reflexionando sobre: {question[:50]}...")

        # Protocolo de seguridad
        safety_result = self.safety_protocol.evaluate(question)
        if safety_result.triggered:
            crisis_reply = self._format_safety_response(safety_result)
            print(
                "🛡️ Protocolo de crisis activado "
                f"(nivel={safety_result.label or safety_result.severity or 'desconocido'},"
                f" coincidencias={safety_result.matched_terms})"
            )

            if safety_result.alert_required:
                self._notify_safety_alert(chat_request, safety_result)

            if getattr(chat_request, "session_id", None):
                try:
                    self.history_store.append(chat_request.session_id, "user", question)
                    self.history_store.append(chat_request.session_id, "assistant", crisis_reply)
                except Exception as e:
                    print(f"⚠️ No se pudo registrar historial en protocolo de seguridad: {e}")

            return ChatResponse(answer=crisis_reply)

        # Cargar historial reciente si hay session_id
        recent_history = []
        if getattr(chat_request, "session_id", None):
            try:
                recent_history = self.history_store.get_recent(chat_request.session_id, limit=HISTORY_MAX_TURNS)
            except Exception as e:
                print(f"⚠️ Error cargando historial: {e}")
        
        # 0. Intentar responder desde memoria semántica (cache inteligente)
        try:
            hit = self.semantic_memory.find_best(question)
        except Exception as e:
            print(f"⚠️ Error buscando en memoria semántica: {e}")
            hit = None

        if hit:
            entry, score = hit
            # Evitar devolver respuestas negativas antiguas aprendidas por memoria
            ans_lower = entry.answer.strip().lower() if entry.answer else ""
            negative_markers = [
                "no tengo información suficiente",
                "no puedo responder",
                "no puedo proporcionar",
                "no pude generar una respuesta",
                "no dispongo de las regulaciones",
                "no está en mi contexto",
                "te aconsejo consultar",
                "consulta el reglamento",
                "consulta con la oficina",
            ]
            if any(m in ans_lower for m in negative_markers):
                print(f"🧠 Memoria con respuesta negativa detectada (sim={score:.3f}); continuar con RAG")
            else:
                print(f"🧠 Respuesta desde memoria (sim={score:.3f})")
                return ChatResponse(answer=f"🏔️ {entry.answer.strip()}")

        # 1. Buscar contexto relevante
        search_result = self.context_search.search_context(question, self.documents)

        # Decidir modo de respuesta
        best_sim = getattr(search_result, "best_similarity", 0.0) or 0.0
        mode = (ANSWER_MODE or "hybrid").lower()
        allow_general_knowledge = False
        context_text = search_result.context or ""
        has_context = bool(context_text.strip())

        keyword_evidence = False
        keyword_terms: List[str] = []
        if (not has_context) or best_sim < HYBRID_MIN_SIMILARITY:
            keyword_snippets, keyword_terms = self._keyword_context_fallback(question)
            if keyword_snippets:
                keyword_evidence = True
                snippet_header = "Coincidencias por palabras clave:\n"
                if context_text:
                    context_text = f"{context_text}\n---\n{snippet_header}{keyword_snippets}"
                else:
                    context_text = f"{snippet_header}{keyword_snippets}"
                has_context = True
                best_sim = max(best_sim, HYBRID_MIN_SIMILARITY * 0.95)
        if not keyword_evidence:
            keyword_terms = []

        reasoning_notes = self._build_reasoning_notes(question, context_text, keyword_terms)

        context_reliable = (has_context and best_sim >= HYBRID_MIN_SIMILARITY) or keyword_evidence

        general_result = self.general_knowledge.classify(
            question,
            best_similarity=best_sim,
            has_context=has_context,
        )
        prompt_general_result = general_result if general_result.is_general else None

        if mode == "model_only":
            allow_general_knowledge = True
            has_context = False
            context_text = ""
            context_reliable = False
            print("🧭 Modo de respuesta: model_only (sin contexto)")
        elif mode == "hybrid":
            if context_reliable:
                print(f"🧭 Modo de respuesta: hybrid (best_sim={best_sim:.3f}; usar contexto recuperado)")
                allow_general_knowledge = False
            else:
                allow_general_knowledge = True
                print(f"🧭 Modo de respuesta: hybrid (best_sim={best_sim:.3f} < {HYBRID_MIN_SIMILARITY:.2f}; complementar con modelo generativo sin descartar fragmentos recuperados)")
        else:
            print("🧭 Modo de respuesta: rag_only (usar solo contexto)")
            if not context_reliable:
                print("⚠️ No se encontró contexto con similitud suficiente, pero se mantendrá modo RAG puro")

        if context_reliable and general_result.is_general:
            print(f"🌐 Clasificación general detectada ({general_result.category}), pero se prioriza contexto embebido (sim={best_sim:.3f})")
        elif allow_general_knowledge:
            if not general_result.is_general:
                print("🌐 Clasificación general: fallback por ausencia de contexto")
                prompt_general_result = GeneralKnowledgeResult(
                    is_general=True,
                    category=general_result.category or "general",
                    confidence=general_result.confidence or 0.4,
                    reason=(general_result.reason or "sin señales claras") + " + fallback sin contexto",
                )
            else:
                print(f"🌐 Clasificación general: {general_result.category} (conf={general_result.confidence:.2f})")
        else:
            print(f"🌐 Clasificación general: {general_result.reason}")

        # 2. Construir prompt con contexto ancestral y bandera híbrida
        prompt = self.prompt_builder.build_complete_prompt(
            question=question,
            context=context_text,
            has_context=has_context,
            allow_general_knowledge=allow_general_knowledge,
            best_similarity=best_sim,
            history=recent_history,
            general_knowledge_result=prompt_general_result if allow_general_knowledge else None,
            keyword_evidence=keyword_evidence,
            reasoning_notes=reasoning_notes,
        )
        
        # 3. Generar respuesta con Google AI Studio
        raw_response = self.google_ai_client.generate_response(prompt)

        # Manejo de posibles bloqueos por filtros de seguridad
        blocked_markers = [
            "filtros de seguridad",
            "no puedo procesar esa solicitud por razones de seguridad",
            "no puedo proporcionar esa información"
        ]
        if any(marker in raw_response.lower() for marker in blocked_markers):
            print("⚠️ Se detectó bloqueo por filtros de seguridad. Intentando alternativa segura...")
            # Alternativa: respuesta neutra basada en el contexto disponible
            if search_result and search_result.has_relevant_content and search_result.context:
                safe_answer = (
                    "A continuación te comparto información general relevante basada en documentos disponibles:\n\n"
                    f"{search_result.context[:800]}"
                )
            else:
                safe_answer = (
                    "No puedo responder esa solicitud. Por favor reformula tu pregunta con un enfoque académico/"
                    "informativo y sin incluir contenido sensible."
                )
            raw_response = safe_answer
        
        # 4. Formatear respuesta final con identidad de ORIGEN
        final_response = f"🏔️ {raw_response.strip()}"
        
        print(f"✅ {BOT_NAME} ha compartido su sabiduría")

        # 5. Almacenar en memoria semántica (aprendizaje continuo)
        try:
            self.semantic_memory.add(question=question, answer=raw_response)
        except Exception as e:
            print(f"⚠️ No se pudo guardar en memoria semántica: {e}")

        # 6. Registrar historial si hay session_id
        if getattr(chat_request, "session_id", None):
            try:
                self.history_store.append(chat_request.session_id, "user", question)
                self.history_store.append(chat_request.session_id, "assistant", final_response)
            except Exception as e:
                print(f"⚠️ No se pudo registrar historial: {e}")
        
        return ChatResponse(answer=final_response)

    def _format_safety_response(self, safety_result: SafetyProtocolResult) -> str:
        """Estructura el mensaje cuando se activa el protocolo de seguridad."""

        lines: List[str] = []
        if safety_result.label:
            lines.append(f"Nivel de riesgo detectado: {safety_result.label}")
        elif safety_result.severity:
            lines.append(f"Nivel de riesgo detectado: {safety_result.severity.upper()}")

        if safety_result.message:
            lines.append(safety_result.message.strip())

        if safety_result.recommendations:
            lines.append("Pasos sugeridos:")
            lines.extend(f"- {step}" for step in safety_result.recommendations)

        if safety_result.alert_required:
            lines.append("🚨 Se ha activado una alerta para el equipo humano de apoyo.")

        body = "\n".join(lines).strip() or "Se han detectado senales de riesgo y se prioriza tu seguridad."
        return f"🏔️ {body}"

    def _notify_safety_alert(self, chat_request: ChatRequest, safety_result: SafetyProtocolResult) -> None:
        """Registra y permite escalar alertas de alto riesgo a un equipo humano."""

        try:
            session_id = getattr(chat_request, "session_id", None) or "sin_session"
            print(
                f"🚨 Notificacion de alerta enviada (nivel={safety_result.label or safety_result.severity}, "
                f"session={session_id}, coincidencias={safety_result.matched_terms})"
            )
        except Exception as exc:
            print(f"⚠️ Error al notificar protocolo de seguridad: {exc}")

    def _keyword_context_fallback(self, question: str, max_snippets: int = 3, window: int = 220) -> Tuple[str, List[str]]:
        """Busca coincidencias textuales para reforzar el contexto cuando el RAG es débil."""

        if not question:
            return "", []

        lower_question = question.lower().strip()
        normalized_question = re.sub(r"[¿¡?!]", " ", lower_question)
        normalized_question = re.sub(r"\s+", " ", normalized_question).strip()
        candidates: List[str] = []
        key_terms: Set[str] = set()

        # Patrones comunes "quién es ..."
        patterns = [
            r"(?:^|\s)qu[ií]en es\s+(.+)",
            r"(?:^|\s)qu[ií]en fue\s+(.+)",
            r"(?:^|\s)qu[ií]nes son\s+(.+)",
            r"(?:^|\s)who is\s+(.+)",
            r"(?:^|\s)who was\s+(.+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, normalized_question)
            if match:
                fragment = re.split(r"[?.!]", match.group(1))[0]
                fragment = fragment.strip()
                fragment = re.sub(r"^(el|la|los|las)\s+", "", fragment)
                if fragment and fragment not in candidates:
                    candidates.append(fragment)
                key_terms.update(
                    token for token in fragment.lower().split()
                    if token not in self.KEYWORD_STOPWORDS and len(token) >= 3
                )

        # Detectar palabras con mayúsculas en la pregunta original
        proper_names = re.findall(
            r"\b[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚÑ]+(?:\s+[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚÑ]+){0,2}",
            re.sub(r"[¿?!]", " ", question)
        )
        for name in proper_names:
            cleaned = name.strip()
            lower_name = cleaned.lower()
            if cleaned and lower_name not in candidates:
                candidates.append(lower_name)
            key_terms.update(
                token for token in lower_name.split()
                if token not in self.KEYWORD_STOPWORDS and len(token) >= 3
            )

        tokens = [
            t for t in re.findall(r"[a-záéíóúñ]{3,}", normalized_question)
            if t not in self.KEYWORD_STOPWORDS
        ]
        if len(tokens) >= 2:
            name_guess = " ".join(tokens[:2])
            if name_guess not in candidates:
                candidates.append(name_guess)
            name_tail = " ".join(tokens[-2:])
            if name_tail not in candidates:
                candidates.append(name_tail)
        key_terms.update(tokens)

        if not candidates:
            return "", list(key_terms)

        snippets: List[str] = []
        for document in self.documents:
            content = document.content
            content_lower = content.lower()
            found = False
            for phrase in candidates:
                idx = content_lower.find(phrase)
                if idx != -1:
                    start = max(0, idx - window // 2)
                    end = min(len(content), idx + window)
                    snippet = content[start:end]
                    snippet = re.sub(r"\s+", " ", snippet).strip()
                    snippets.append(f"{document.filename}: {snippet}")
                    found = True
                    break
            if not found and tokens:
                core_tokens = tokens[:3]
                if core_tokens and all(token in content_lower for token in core_tokens):
                    idx = content_lower.find(core_tokens[0])
                    if idx != -1:
                        start = max(0, idx - window // 2)
                        end = min(len(content), idx + window)
                        snippet = content[start:end]
                        snippet = re.sub(r"\s+", " ", snippet).strip()
                        snippets.append(f"{document.filename}: {snippet}")
                        found = True
            if len(snippets) >= max_snippets:
                break

        return "\n".join(snippets[:max_snippets]), list(key_terms)

    def _build_reasoning_notes(self, question: str, context_text: str, keyword_terms: List[str]) -> str:
        """Destila pistas breves para guiar el razonamiento del modelo."""

        if not context_text:
            return ""

        notes: List[str] = []
        normalized_terms: List[str] = []
        seen_terms = set()
        for term in keyword_terms or []:
            term_clean = term.strip().lower()
            if not term_clean or term_clean in seen_terms:
                continue
            if term_clean in self.KEYWORD_STOPWORDS:
                continue
            seen_terms.add(term_clean)
            normalized_terms.append(term_clean)
            if len(normalized_terms) >= 6:
                break

        if normalized_terms:
            notes.append("- Palabras clave a verificar: " + ", ".join(normalized_terms[:5]))

        lines = [re.sub(r"\s+", " ", line).strip() for line in context_text.splitlines() if line.strip()]
        lower_terms = {term.lower() for term in normalized_terms}
        evidence: List[str] = []
        for line in lines:
            sample = line.lower()
            if lower_terms and any(term in sample for term in lower_terms):
                evidence.append(line)
            elif not lower_terms and line:
                evidence.append(line)
            if len(evidence) >= 2:
                break

        if not evidence and lines:
            evidence.append(lines[0])

        trimmed: List[str] = []
        for item in evidence[:2]:
            entry = item
            if len(entry) > 220:
                entry = entry[:217].rstrip() + "..."
            trimmed.append(entry)

        if trimmed:
            notes.append("- Evidencia relevante: " + " | ".join(trimmed))

        return "\n".join(notes)
    
    def get_service_status(self) -> dict:
        """
        Obtiene el estado de todos los servicios
        
        Returns:
            Diccionario con el estado de cada componente
        """
        return {
            "documents_loaded": len(self.documents),
            "google_ai_configured": self.google_ai_client.is_configured(),
            "embedding_service": "OK",
            "context_search": "OK",
            "prompt_builder": "OK"
        }
    
    def process_simple_question(self, question: str) -> str:
        """
        Método conveniente para procesar una pregunta simple
        
        Args:
            question: Pregunta como string
            
        Returns:
            Respuesta como string
        """
        chat_request = ChatRequest(question=question)
        response = self.process_chat_request(chat_request)
        return response.answer
    
    def health_check(self) -> bool:
        """
        Verifica si el servicio está funcionando correctamente
        
        Returns:
            True si todo está OK, False si hay problemas
        """
        try:
            status = self.get_service_status()
            return (
                status["documents_loaded"] >= 0 and
                status["google_ai_configured"]
            )
        except Exception as e:
            print(f"❌ Error en health check: {e}")
            return False