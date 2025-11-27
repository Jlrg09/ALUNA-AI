"""
Gestor de conversaciones para ORIGEN
Maneja la creación, guardado y recuperación de conversaciones
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import uuid

class ConversationManager:
    """Gestiona las conversaciones del usuario"""
    
    def __init__(self, storage_path: str = "conversations"):
        """
        Inicializa el gestor de conversaciones
        
        Args:
            storage_path: Ruta donde se guardarán las conversaciones
        """
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        self.conversations_file = os.path.join(storage_path, "conversations.json")
        self._ensure_storage()
    
    def _ensure_storage(self):
        """Asegura que existe el archivo de almacenamiento"""
        if not os.path.exists(self.conversations_file):
            self._save_conversations([])
    
    def _load_conversations(self) -> List[Dict]:
        """Carga todas las conversaciones"""
        try:
            with open(self.conversations_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error cargando conversaciones: {e}")
            return []
    
    def _save_conversations(self, conversations: List[Dict]):
        """Guarda todas las conversaciones"""
        try:
            with open(self.conversations_file, 'w', encoding='utf-8') as f:
                json.dump(conversations, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando conversaciones: {e}")
    
    def create_conversation(self) -> Dict:
        """
        Crea una nueva conversación
        
        Returns:
            Dict con los datos de la nueva conversación
        """
        conversation = {
            "id": str(uuid.uuid4()),
            "title": "Nueva conversación",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": [],
            "first_message_preview": ""
        }
        
        conversations = self._load_conversations()
        conversations.insert(0, conversation)  # Insertar al inicio
        self._save_conversations(conversations)
        
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """
        Obtiene una conversación por su ID
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            Dict con los datos de la conversación o None si no existe
        """
        conversations = self._load_conversations()
        for conv in conversations:
            if conv["id"] == conversation_id:
                return conv
        return None
    
    def get_all_conversations(self, limit: int = 50) -> List[Dict]:
        """
        Obtiene todas las conversaciones
        
        Args:
            limit: Número máximo de conversaciones a devolver
            
        Returns:
            Lista de conversaciones ordenadas por fecha de actualización
        """
        conversations = self._load_conversations()
        # Ordenar por fecha de actualización (más reciente primero)
        conversations.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return conversations[:limit]
    
    def add_message(self, conversation_id: str, message_type: str, content: str) -> bool:
        """
        Agrega un mensaje a una conversación
        
        Args:
            conversation_id: ID de la conversación
            message_type: Tipo de mensaje ('user' o 'ai')
            content: Contenido del mensaje
            
        Returns:
            True si se agregó correctamente, False en caso contrario
        """
        conversations = self._load_conversations()
        
        for conv in conversations:
            if conv["id"] == conversation_id:
                message = {
                    "type": message_type,
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                }
                conv["messages"].append(message)
                conv["updated_at"] = datetime.now().isoformat()
                
                # Si es el primer mensaje del usuario, generar título
                if message_type == "user" and len([m for m in conv["messages"] if m["type"] == "user"]) == 1:
                    conv["title"] = self._generate_title(content)
                    conv["first_message_preview"] = content[:100]
                
                self._save_conversations(conversations)
                return True
        
        return False
    
    def _generate_title(self, first_message: str) -> str:
        """
        Genera un título para la conversación basado en el primer mensaje
        
        Args:
            first_message: Primer mensaje del usuario
            
        Returns:
            Título generado
        """
        # Limpiar y truncar el mensaje
        title = first_message.strip()
        
        # Si es muy corto, usarlo tal cual
        if len(title) <= 50:
            return title
        
        # Si es más largo, truncar de forma inteligente
        # Intentar cortar en una palabra completa
        truncated = title[:50]
        last_space = truncated.rfind(' ')
        
        if last_space > 20:  # Solo cortar en espacio si no es muy al inicio
            return truncated[:last_space] + "..."
        else:
            return truncated + "..."
    
    def update_title(self, conversation_id: str, title: str) -> bool:
        """
        Actualiza el título de una conversación
        
        Args:
            conversation_id: ID de la conversación
            title: Nuevo título
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        conversations = self._load_conversations()
        
        for conv in conversations:
            if conv["id"] == conversation_id:
                conv["title"] = title
                conv["updated_at"] = datetime.now().isoformat()
                self._save_conversations(conversations)
                return True
        
        return False
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Elimina una conversación
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        conversations = self._load_conversations()
        original_length = len(conversations)
        
        conversations = [c for c in conversations if c["id"] != conversation_id]
        
        if len(conversations) < original_length:
            self._save_conversations(conversations)
            return True
        
        return False
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """
        Limpia los mensajes de una conversación sin eliminarla
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            True si se limpió correctamente, False en caso contrario
        """
        conversations = self._load_conversations()
        
        for conv in conversations:
            if conv["id"] == conversation_id:
                conv["messages"] = []
                conv["title"] = "Nueva conversación"
                conv["first_message_preview"] = ""
                conv["updated_at"] = datetime.now().isoformat()
                self._save_conversations(conversations)
                return True
        
        return False
