#!/usr/bin/env python3
"""
Script para generar embeddings de todos los documentos en la carpeta de conocimiento
"""
import os
import sys
from rag.document_processor import DocumentProcessor
from rag.embedding_manager import EmbeddingManager
from config import KNOWLEDGE_DIR, EMBEDDINGS_FILE

def main():
    """Función principal para generar embeddings"""
    print("🚀 Iniciando generación de embeddings...")
    print(f"📁 Directorio de documentos: {KNOWLEDGE_DIR}")
    print(f"💾 Archivo de embeddings: {EMBEDDINGS_FILE}")
    print("-" * 50)
    
    # Verificar que existe el directorio de documentos
    if not os.path.exists(KNOWLEDGE_DIR):
        print(f"❌ Error: El directorio {KNOWLEDGE_DIR} no existe")
        return False
    
    # Inicializar componentes
    processor = DocumentProcessor()
    embedding_manager = EmbeddingManager()
    
    # Cargar documentos
    print("📚 Cargando documentos...")
    documents = processor.load_documents()
    
    if not documents:
        print("⚠️ No se encontraron documentos para procesar")
        return False
    
    print(f"✅ Se cargaron {len(documents)} documentos:")
    for doc in documents:
        print(f"   - {doc.filename}")
    
    print("-" * 50)
    
    # Generar embeddings
    print("🤖 Generando embeddings...")
    embedding_data = embedding_manager.generate_embeddings(documents)
    
    if embedding_data and len(embedding_data.embeddings) > 0:
        print("✅ ¡Embeddings generados exitosamente!")
        print(f"📊 Total de embeddings: {len(embedding_data.embeddings)}")
        print(f"💾 Guardados en: {EMBEDDINGS_FILE}")
        return True
    else:
        print("❌ Error al generar embeddings")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 ¡Proceso completado exitosamente!")
        else:
            print("\n❌ El proceso falló")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
