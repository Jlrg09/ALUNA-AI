"""
Script de prueba para verificar funcionalidad
"""
import requests
import json

def test_api():
    """Prueba las APIs principales"""
    base_url = "http://localhost:5000"
    
    print("🧪 Probando APIs de ORIGEN...")
    print("-" * 40)
    
    # Probar estado
    try:
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ Estado del sistema:")
            print(f"   - Estado: {data['status']}")
            print(f"   - Documentos: {data['documents_count']}")
            print(f"   - Índice: {data['search_index_size']} palabras")
        else:
            print(f"❌ Error en estado: {response.status_code}")
    except Exception as e:
        print(f"❌ Error conectando: {e}")
        return
    
    print()
    
    # Probar lista de documentos
    try:
        response = requests.get(f"{base_url}/api/documents")
        if response.status_code == 200:
            data = response.json()
            print("📚 Documentos disponibles:")
            for doc in data['documents']:
                print(f"   - {doc['filename']} ({doc['size']} chars)")
        else:
            print(f"❌ Error en documentos: {response.status_code}")
    except Exception as e:
        print(f"❌ Error obteniendo documentos: {e}")
    
    print()
    
    # Probar chat
    test_questions = [
        "¿Qué es ORIGEN?",
        "Universidad del Magdalena",
        "Deiber Alexander",
        "programas académicos"
    ]
    
    print("💬 Probando chat:")
    for question in test_questions:
        try:
            response = requests.post(
                f"{base_url}/api/chat",
                json={"question": question},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data['answer'][:100] + "..." if len(data['answer']) > 100 else data['answer']
                print(f"   ❓ {question}")
                print(f"   ✅ {answer}")
                print()
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("🎉 Pruebas completadas")

if __name__ == "__main__":
    test_api()
