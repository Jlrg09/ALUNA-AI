"""
Gestor de embeddings para el sistema RAG
"""
import os
import pickle
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from models import EmbeddingData, Document
from config import EMBEDDINGS_FILE, EMBEDDING_MODEL_NAME, CHUNK_SIZE, CHUNK_OVERLAP


class EmbeddingManager:
    """Gestor de embeddings para documentos"""
    
    def __init__(self):
        """Inicializa el gestor de embeddings"""
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        print(f"🤖 Modelo de embeddings cargado: {EMBEDDING_MODEL_NAME}")
    
    def save_embeddings(self, embedding_data: EmbeddingData) -> None:
        """
        Guarda los embeddings en archivo
        
        Args:
            embedding_data: Datos de embeddings a guardar
        """
        try:
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(EMBEDDINGS_FILE) or '.', exist_ok=True)
            
            with open(EMBEDDINGS_FILE, "wb") as f:
                pickle.dump(embedding_data.to_dict(), f)
            print(f"💾 Embeddings guardados en: {EMBEDDINGS_FILE}")
        except Exception as e:
            print(f"❌ Error guardando embeddings: {e}")
    
    def load_embeddings(self) -> Optional[EmbeddingData]:
        """
        Carga los embeddings desde archivo
        
        Returns:
            Datos de embeddings o None si no existen
        """
        if not os.path.exists(EMBEDDINGS_FILE):
            print(f"⚠️ Archivo de embeddings no existe: {EMBEDDINGS_FILE}")
            return None
            
        try:
            with open(EMBEDDINGS_FILE, "rb") as f:
                data = pickle.load(f)
            print(f"📥 Embeddings cargados desde: {EMBEDDINGS_FILE}")
            return EmbeddingData.from_dict(data)
        except Exception as e:
            print(f"❌ Error cargando embeddings: {e}")
            return None
    
    def generate_embeddings(self, documents: List[Document]) -> EmbeddingData:
        """
        Genera embeddings para una lista de documentos (con chunking)
        
        Args:
            documents: Lista de documentos
            
        Returns:
            Datos de embeddings generados
        """
        if not documents:
            print("⚠️ No hay documentos para generar embeddings")
            return EmbeddingData(embeddings=[], filenames=[], texts=[])
        
        # Crear chunks por documento para mejorar el recall y la precisión
        def chunk_text(text: str, size: int, overlap: int) -> List[str]:
            if size <= 0:
                return [text]
            chunks = []
            start = 0
            n = len(text)
            step = max(1, size - overlap)
            while start < n:
                end = min(n, start + size)
                chunk = text[start:end]
                # Evitar añadir chunks casi vacíos consecutivos
                if chunk.strip():
                    chunks.append(chunk)
                if end == n:
                    break
                start += step
            return chunks if chunks else [text]

        texts: List[str] = []
        filenames: List[str] = []
        for doc in documents:
            doc_chunks = chunk_text(doc.content, CHUNK_SIZE, CHUNK_OVERLAP)
            texts.extend(doc_chunks)
            filenames.extend([doc.filename] * len(doc_chunks))
        
        try:
            print(f"🔄 Generando embeddings para {len(documents)} documentos...")
            doc_embeddings = self.model.encode(texts, show_progress_bar=True)
            
            embedding_data = EmbeddingData(
                embeddings=doc_embeddings,
                filenames=filenames,
                texts=texts,
                meta={
                    "strategy": "chunks_v1",
                    "chunk_size": CHUNK_SIZE,
                    "chunk_overlap": CHUNK_OVERLAP,
                    "doc_count": len(documents),
                }
            )
            
            # Guardar automáticamente
            self.save_embeddings(embedding_data)
            print("✅ Embeddings generados y guardados exitosamente")
            
            return embedding_data
            
        except Exception as e:
            print(f"❌ Error generando embeddings: {e}")
            return EmbeddingData(embeddings=[], filenames=[], texts=[])
    
    def get_or_generate_embeddings(self, documents: List[Document]) -> Optional[EmbeddingData]:
        """
        Obtiene embeddings existentes o los genera si no existen o están desactualizados
        
        Args:
            documents: Lista de documentos actuales
            
        Returns:
            Datos de embeddings actualizados
        """
        embedding_data = self.load_embeddings()

        # Verificar si necesitamos regenerar
        current_files = set(doc.filename for doc in documents)
        meta = getattr(embedding_data, "meta", {}) if embedding_data else {}
        strategy_ok = meta.get("strategy") == "chunks_v1" and \
            meta.get("chunk_size") == CHUNK_SIZE and \
            meta.get("chunk_overlap") == CHUNK_OVERLAP

        needs_regeneration = (
            embedding_data is None or
            set(embedding_data.filenames) != current_files or
            not strategy_ok
        )
        
        if needs_regeneration:
            print("🔄 Regenerando embeddings debido a cambios en documentos...")
            embedding_data = self.generate_embeddings(documents)
        else:
            print("✅ Usando embeddings existentes")
        
        return embedding_data
    
    def encode_query(self, query: str):
        """
        Codifica una consulta a embedding
        
        Args:
            query: Texto de la consulta
            
        Returns:
            Embedding de la consulta
        """
        return self.model.encode([query])