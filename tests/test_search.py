#!/usr/bin/env python3
"""
Script para probar la búsqueda de contexto con los embeddings generados
"""
import sys
from rag.context_search import ContextSearchService
from rag.document_processor import DocumentProcessor

def main():
    """Función principal para probar búsqueda"""
    print("🔍 Probando sistema de búsqueda con embeddings...")
    print("-" * 50)
    
    # Cargar documentos
    processor = DocumentProcessor()
    documents = processor.load_documents()
    
    if not documents:
        print("❌ No se encontraron documentos")
        return False
    
    # Inicializar búsqueda de contexto
    try:
        search = ContextSearchService()
        print("✅ Sistema de búsqueda inicializado")
        print(f"📚 Documentos cargados: {len(documents)}")
    except Exception as e:
        print(f"❌ Error inicializando búsqueda: {e}")
        return False
    
    # Consultas de prueba
    test_queries = [
        "¿Qué es ORIGEN?",
        "Universidad del Magdalena",
        "estatuto general",
        "ministros de educación",
        "inteligencia artificial"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Consulta {i}: '{query}'")
        print("-" * 30)
        
        try:
            # Buscar contexto relevante
            result = search.search_context(query, documents, max_results=2)
            
            if result.has_relevant_content:
                print(f"✅ Se encontraron {len(result.relevant_indices)} resultados relevantes:")
                context_parts = result.context.split('\n\n')
                for j, part in enumerate(context_parts, 1):
                    if part.strip():
                        lines = part.split('\n')
                        header = lines[0] if lines else ""
                        content_preview = '\n'.join(lines[1:3]) if len(lines) > 1 else ""
                        print(f"   {j}. {header}")
                        print(f"      📝 {content_preview}")
                        print()
            else:
                print("⚠️ No se encontraron resultados relevantes")
                
        except Exception as e:
            print(f"❌ Error en búsqueda: {e}")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("🎉 ¡Pruebas de búsqueda completadas!")
        else:
            print("❌ Las pruebas fallaron")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)
