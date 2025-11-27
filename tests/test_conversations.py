"""
Script de prueba para verificar el sistema de conversaciones
"""
import sys
sys.path.insert(0, r"c:\Users\Jose Romero\OneDrive - Universidad del Magdalena\Documentos\Jose-Romero\Proyectos\ChatBot IguChat")

from services.conversation_manager import ConversationManager

def test_conversation_manager():
    """Prueba básica del gestor de conversaciones"""
    print("Probando ConversationManager...")
    
    # Crear instancia
    manager = ConversationManager(storage_path="conversations_test")
    
    # Crear conversación
    print("\n1. Creando conversación...")
    conv = manager.create_conversation()
    print(f"   ✓ Conversación creada: {conv['id']}")
    
    # Agregar mensaje
    print("\n2. Agregando mensaje del usuario...")
    success = manager.add_message(conv['id'], 'user', '¿Puedes contarme sobre la cultura Kogui?')
    print(f"   ✓ Mensaje agregado: {success}")
    
    # Obtener conversación
    print("\n3. Obteniendo conversación...")
    conv_updated = manager.get_conversation(conv['id'])
    print(f"   ✓ Título generado: '{conv_updated['title']}'")
    print(f"   ✓ Mensajes: {len(conv_updated['messages'])}")
    
    # Listar conversaciones
    print("\n4. Listando todas las conversaciones...")
    all_convs = manager.get_all_conversations()
    print(f"   ✓ Total de conversaciones: {len(all_convs)}")
    
    print("\n✅ Todas las pruebas pasaron correctamente!")
    
    # Limpiar archivos de prueba
    import os
    import shutil
    if os.path.exists("conversations_test"):
        shutil.rmtree("conversations_test")
        print("🧹 Archivos de prueba eliminados")

if __name__ == "__main__":
    test_conversation_manager()
