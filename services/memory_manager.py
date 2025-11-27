"""
Administrador de Memoria Semántica (cache inteligente de Q/A)
"""
from __future__ import annotations
import os
import pickle
from typing import List, Optional, Tuple
import numpy as np
from time import time

from models import MemoryEntry
from config import MEMORY_FILE, MEMORY_SIMILARITY_THRESHOLD, MEMORY_TOP_K
from rag.embedding_manager import EmbeddingManager


def _normalize(v: np.ndarray) -> np.ndarray:
    """Normaliza un vector a norma L2; evita división por cero."""
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


class SemanticMemory:
    """Memoria semántica local y persistente para preguntas/respuestas.

    - Usa el mismo modelo de embeddings del sistema para codificar preguntas.
    - Calcula similitud coseno con embeddings normalizados.
    - Persiste en disco (pickle) para uso posterior.
    """

    def __init__(self):
        self.embedding_manager = EmbeddingManager()
        self.entries: List[MemoryEntry] = []
        self._load()

    # ----------------------
    # Persistencia
    # ----------------------
    def _load(self) -> None:
        if not os.path.exists(MEMORY_FILE):
            self.entries = []
            return
        try:
            with open(MEMORY_FILE, "rb") as f:
                data = pickle.load(f)
            # Reconstruir entradas
            self.entries = []
            for item in data:
                emb = np.array(item["embedding"], dtype=np.float32)
                self.entries.append(
                    MemoryEntry(
                        question=item["question"],
                        answer=item["answer"],
                        embedding=_normalize(emb),
                        created_at=item.get("created_at", time()),
                        last_used_at=item.get("last_used_at", time()),
                        usage_count=item.get("usage_count", 0),
                        last_score=item.get("last_score", 0.0),
                    )
                )
        except Exception as e:
            print(f"❌ Error cargando memoria semántica: {e}")
            self.entries = []

    def _save(self) -> None:
        try:
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(MEMORY_FILE) or '.', exist_ok=True)
            
            data = [
                {
                    "question": e.question,
                    "answer": e.answer,
                    "embedding": e.embedding.astype(float).tolist(),
                    "created_at": e.created_at,
                    "last_used_at": e.last_used_at,
                    "usage_count": e.usage_count,
                    "last_score": e.last_score,
                }
                for e in self.entries
            ]
            with open(MEMORY_FILE, "wb") as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"❌ Error guardando memoria semántica: {e}")

    # ----------------------
    # Búsqueda
    # ----------------------
    def encode_question(self, question: str) -> np.ndarray:
        emb = self.embedding_manager.encode_query(question)
        # encode_query devuelve shape (1, D); aplanar
        vec = np.array(emb).reshape(-1)
        return _normalize(vec.astype(np.float32))

    def search(self, query_embedding: np.ndarray, top_k: int = None) -> List[Tuple[int, float]]:
        """Retorna lista de (index, score) ordenada por similitud desc."""
        if top_k is None:
            top_k = MEMORY_TOP_K
        if not self.entries:
            return []
        # Matriz de embeddings normalizados
        M = np.stack([e.embedding for e in self.entries], axis=0)
        scores = M @ query_embedding  # coseno al estar normalizados
        idxs = np.argsort(scores)[-top_k:][::-1]
        return [(int(i), float(scores[int(i)])) for i in idxs]

    def find_best(self, question: str) -> Optional[Tuple[MemoryEntry, float]]:
        q_emb = self.encode_question(question)
        candidates = self.search(q_emb, top_k=MEMORY_TOP_K)
        if not candidates:
            return None
        best_idx, best_score = candidates[0]
        if best_score >= MEMORY_SIMILARITY_THRESHOLD:
            entry = self.entries[best_idx]
            # actualizar metadatos
            entry.usage_count += 1
            entry.last_used_at = time()
            entry.last_score = best_score
            self._save()
            return entry, best_score
        return None

    # ----------------------
    # Inserción/actualización
    # ----------------------
    def add(self, question: str, answer: str, question_embedding: Optional[np.ndarray] = None) -> MemoryEntry:
        # No cachear respuestas negativas/vacías
        text = (answer or "").strip().lower()
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
        if not text or any(m in text for m in negative_markers):
            # saltar persistencia de respuestas poco útiles
            return MemoryEntry(question=question, answer=answer, embedding=np.zeros((1,), dtype=np.float32))

        if question_embedding is None:
            question_embedding = self.encode_question(question)
        # normalizar por seguridad
        question_embedding = _normalize(question_embedding.astype(np.float32))
        entry = MemoryEntry(
            question=question,
            answer=answer,
            embedding=question_embedding,
            created_at=time(),
            last_used_at=time(),
            usage_count=0,
            last_score=0.0,
        )
        self.entries.append(entry)
        self._save()
        return entry

    # ----------------------
    # Utilidades
    # ----------------------
    def stats(self) -> dict:
        return {
            "entries": len(self.entries),
            "threshold": MEMORY_SIMILARITY_THRESHOLD,
            "top_k": MEMORY_TOP_K,
        }

    def clear(self) -> int:
        n = len(self.entries)
        self.entries = []
        self._save()
        return n
