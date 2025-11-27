"""
Servicio de búsqueda de contexto usando embeddings
"""
from typing import List
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from models import Document, SearchResult, EmbeddingData
from config import DEFAULT_TOP_K, MIN_SIMILARITY_THRESHOLD, RETRIEVAL_MAX_FRAGMENT_CHARS
from rag.embedding_manager import EmbeddingManager


class ContextSearchService:
    """Servicio para búsqueda de contexto relevante"""
    
    def __init__(self):
        """Inicializa el servicio de búsqueda"""
        self.embedding_manager = EmbeddingManager()
    
    def search_context(
        self, 
        question: str, 
        documents: List[Document], 
        top_k: int = DEFAULT_TOP_K
    ) -> SearchResult:
        """
        Busca contexto relevante para una pregunta
        
        Args:
            question: Pregunta del usuario
            documents: Lista de documentos disponibles
            top_k: Número máximo de fragmentos relevantes a retornar
            
        Returns:
            Resultado de búsqueda con contexto relevante
        """
        if not documents:
            return SearchResult(
                context="",
                similarity_scores=[],
                relevant_indices=[],
                has_relevant_content=False,
                best_similarity=0.0,
            )
        
        # Obtener o generar embeddings
        embedding_data = self.embedding_manager.get_or_generate_embeddings(documents)
        
        if not embedding_data or len(embedding_data.embeddings) == 0:
            return SearchResult(
                context="",
                similarity_scores=[],
                relevant_indices=[],
                has_relevant_content=False,
                best_similarity=0.0,
            )
        
        # Codificar la pregunta
        question_embedding = self.embedding_manager.encode_query(question)
        
        # Calcular similitudes
        similarities = cosine_similarity(
            question_embedding, 
            embedding_data.embeddings
        )[0]

        # Obtener índices de los fragmentos más relevantes
        top_indices = similarities.argsort()[-top_k:][::-1]
        best_similarity = float(similarities[top_indices[0]]) if len(top_indices) > 0 else 0.0
        
        # Filtrar por umbral de similitud (más permisivo)
        relevant_indices = [
            idx for idx in top_indices 
            if similarities[idx] >= MIN_SIMILARITY_THRESHOLD
        ]

        # Si no hay ningún índice que supere el umbral, tomar al menos el top-1
        if not relevant_indices and len(top_indices) > 0:
            relevant_indices = [top_indices[0]]
        
        # Construir contexto sin citar fuentes ni nombres de archivo
        context_parts = []
        for i, idx in enumerate(relevant_indices):
            text = embedding_data.texts[idx]
            # Truncar fragmento si es demasiado largo
            if len(text) > RETRIEVAL_MAX_FRAGMENT_CHARS:
                text = text[:RETRIEVAL_MAX_FRAGMENT_CHARS]
            context_parts.append(text)
        
        context = "\n\n".join(context_parts)
        has_relevant_content = len(relevant_indices) > 0
        
        return SearchResult(
            context=context,
            similarity_scores=[float(similarities[idx]) for idx in relevant_indices],
            relevant_indices=relevant_indices,
            has_relevant_content=has_relevant_content,
            best_similarity=best_similarity,
        )
    
    def search_context_legacy(
        self, 
        question: str, 
        documents: List[Document], 
        top_k: int = DEFAULT_TOP_K
    ) -> str:
        """
        Versión legacy que retorna solo el contexto como string
        Para compatibilidad con el código existente
        
        Args:
            question: Pregunta del usuario
            documents: Lista de documentos disponibles
            top_k: Número máximo de fragmentos relevantes a retornar
            
        Returns:
            Contexto relevante como string
        """
        result = self.search_context(question, documents, top_k)
        return result.context