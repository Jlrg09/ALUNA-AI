"""
Script para generar embeddings de forma simple
Versión simplificada sin dependencias complejas
"""
import os
import sys
from rag.document_processor import DocumentProcessor
from config import KNOWLEDGE_DIR

def main():
    """Función principal para generar embeddings"""
    print("🚀 Iniciando procesamiento de documentos...")
    print(f"📁 Directorio de documentos: {KNOWLEDGE_DIR}")
    print("-" * 50)
    
    # Verificar que existe el directorio de documentos
    if not os.path.exists(KNOWLEDGE_DIR):
        print(f"❌ Error: El directorio {KNOWLEDGE_DIR} no existe")
        return False
    
    # Inicializar procesador
    try:
        processor = DocumentProcessor()
        print("✅ Procesador de documentos inicializado")
    except Exception as e:
        print(f"❌ Error inicializando procesador: {e}")
        print("💡 Sugerencia: Instala las dependencias con: pip install python-docx PyPDF2")
        return False
    
    # Cargar documentos
    print("📚 Cargando documentos...")
    documents = processor.load_documents()
    
    if not documents:
        print("⚠️ No se encontraron documentos para procesar")
        return False
    
    print(f"✅ Se cargaron {len(documents)} documentos:")
    for doc in documents:
        preview = doc.content[:100] + "..." if len(doc.content) > 100 else doc.content
        print(f"   - {doc.filename}: {preview}")
    
    print("-" * 50)
    print("✅ ¡Documentos procesados exitosamente!")
    print("💡 Para generar embeddings ejecuta: python scripts/generate_embeddings.py")
    return True

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
