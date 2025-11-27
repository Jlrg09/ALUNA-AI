#!/usr/bin/env python3
"""
Script para verificar y mostrar información de los embeddings generados
"""
import os
import pickle
from config import EMBEDDINGS_FILE, KNOWLEDGE_DIR

def main():
    """Función principal para verificar embeddings"""
    print("🔍 Verificando embeddings generados...")
    print(f"📁 Archivo de embeddings: {EMBEDDINGS_FILE}")
    print("-" * 50)
    
    # Verificar que existe el archivo
    if not os.path.exists(EMBEDDINGS_FILE):
        print(f"❌ Error: El archivo {EMBEDDINGS_FILE} no existe")
        print("💡 Ejecuta 'python scripts/generate_embeddings.py' primero")
        return False
    
    try:
        # Cargar embeddings
        with open(EMBEDDINGS_FILE, "rb") as f:
            data = pickle.load(f)
        
        embeddings = data["embeddings"]
        filenames = data["filenames"]
        texts = data["texts"]
        
        print(f"✅ Embeddings cargados exitosamente")
        print(f"📊 Información de los embeddings:")
        print(f"   - Número de documentos: {len(filenames)}")
        print(f"   - Dimensión de embeddings: {embeddings.shape[1] if len(embeddings.shape) > 1 else 'N/A'}")
        print(f"   - Tamaño del archivo: {os.path.getsize(EMBEDDINGS_FILE)} bytes")
        
        print("\n📚 Documentos incluidos:")
        for i, filename in enumerate(filenames):
            text_preview = texts[i][:100] + "..." if len(texts[i]) > 100 else texts[i]
            print(f"   {i+1}. {filename}")
            print(f"      📝 Texto: {text_preview}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error al cargar embeddings: {e}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("🎉 ¡Verificación completada!")
        else:
            print("❌ La verificación falló")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
