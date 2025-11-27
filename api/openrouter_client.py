"""
Cliente para la API de OpenRouter
"""
import requests
from typing import List, Dict, Any, Optional
from models import OpenRouterRequest
from config import (
    OPENROUTER_API_KEY, 
    OPENROUTER_MODEL, 
    BOT_NAME, 
    UNIVERSIDAD,
    MAX_TOKENS,
    TEMPERATURE
)


class OpenRouterClient:
    """Cliente para interactuar con la API de OpenRouter"""
    
    def __init__(self):
        """Inicializa el cliente de OpenRouter"""
        self.api_key = OPENROUTER_API_KEY
        self.model = OPENROUTER_MODEL
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
        if not self.api_key:
            print("⚠️ OPENROUTER_API_KEY no configurada")
        if not self.model:
            print("⚠️ OPENROUTER_MODEL no configurado")
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Obtiene los headers para las solicitudes
        
        Returns:
            Headers de la solicitud
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def _build_system_message(self) -> str:
        """
        Construye el mensaje del sistema
        
        Returns:
            Mensaje del sistema para el chatbot
        """
        return (
            f"Eres {BOT_NAME}, un chatbot institucional de la {UNIVERSIDAD}. "
            f"Responde solo sobre temas relacionados con esta universidad. "
            f"Sé breve y directo. Si no tienes información suficiente, "
            f"sugiere a qué dependencia consultar."
        )
    
    def _create_request_payload(self, user_message: str) -> Dict[str, Any]:
        """
        Crea el payload para la solicitud
        
        Args:
            user_message: Mensaje del usuario
            
        Returns:
            Payload de la solicitud
        """
        return {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": self._build_system_message()
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE
        }
    
    def generate_response(self, prompt: str) -> str:
        """
        Genera una respuesta usando OpenRouter
        
        Args:
            prompt: Prompt completo para el modelo
            
        Returns:
            Respuesta generada por el modelo
        """
        if not self.api_key or not self.model:
            return "❌ Configuración de OpenRouter incompleta. Verifica las variables de entorno."
        
        try:
            headers = self._get_headers()
            payload = self._create_request_payload(prompt)
            
            print(f"🤖 Enviando solicitud a OpenRouter...")
            response = requests.post(
                self.base_url, 
                headers=headers, 
                json=payload, 
                timeout=30
            )
            
            if response.ok:
                response_data = response.json()
                content = response_data["choices"][0]["message"]["content"]
                print(f"✅ Respuesta recibida de OpenRouter")
                return content
            else:
                error_msg = f"❌ OpenRouter Error: {response.status_code} - {response.text}"
                print(error_msg)
                return "Lo siento, no pude procesar tu pregunta en este momento."
                
        except requests.exceptions.Timeout:
            print("❌ Timeout en la solicitud a OpenRouter")
            return "Lo siento, la solicitud tardó demasiado. Intenta nuevamente."
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión con OpenRouter: {e}")
            return "Lo siento, hay problemas de conexión. Intenta más tarde."
            
        except Exception as e:
            print(f"❌ Error inesperado en OpenRouter: {e}")
            return "Lo siento, ocurrió un error técnico."
    
    def is_configured(self) -> bool:
        """
        Verifica si el cliente está correctamente configurado
        
        Returns:
            True si está configurado, False en caso contrario
        """
        return bool(self.api_key and self.model)