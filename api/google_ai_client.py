"""
Cliente para la API de Google AI Studio (Gemini)
"""
import google.generativeai as genai
import time
import random
from typing import Dict, Any, Optional
from config import (
    GOOGLE_AI_API_KEY,
    GOOGLE_AI_MODEL,
    BOT_NAME,
    UNIVERSIDAD,
    BOT_CONTEXT,
    MAX_TOKENS,
    TEMPERATURE,
    AI_SAFETY_MODE,
    get_google_safety_settings,
)


class GoogleAIClient:
    """Cliente para interactuar con Google AI Studio (Gemini)"""
    
    def __init__(self):
        """Inicializa el cliente de Google AI Studio"""
        self.api_key = GOOGLE_AI_API_KEY
        self.model_name = GOOGLE_AI_MODEL
        self.model = None
        
        if not self.api_key:
            print("⚠️ GOOGLE_AI_API_KEY no configurada")
            return
            
        if not self.model_name:
            print("⚠️ GOOGLE_AI_MODEL no configurado")
            return
            
        try:
            # Configurar la API key
            genai.configure(api_key=self.api_key)
            
            # Verificar y ajustar el modelo si es necesario
            self.model_name = self._get_available_model()
            
            # Configurar el modelo con parámetros optimizados para velocidad
            generation_config = {
                "temperature": TEMPERATURE,
                "max_output_tokens": MAX_TOKENS,
                "top_p": 0.95,  # Ajustado para mejor velocidad
                "top_k": 20,    # Reducido para mayor velocidad
                "candidate_count": 1,  # Solo una respuesta para mayor velocidad
            }
            
            # Configuración de seguridad en función del modo elegido en .env
            safety_settings = get_google_safety_settings()
            
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=generation_config,
                safety_settings=safety_settings,
                system_instruction=self._build_system_instruction()
            )
            
            print(
                f"🤖 Cliente Google AI inicializado - Modelo: {self.model_name} | "
                f"Seguridad: {AI_SAFETY_MODE}"
            )
            
        except Exception as e:
            print(f"❌ Error inicializando Google AI: {e}")
            self.model = None
    
    def _build_system_instruction(self) -> str:
        """
        Construye las instrucciones del sistema para ORIGEN
        
        Returns:
            Instrucciones del sistema que incorporan sabiduría ancestral y conocimiento moderno
        """
        peoples_str = ", ".join(BOT_CONTEXT["peoples"])
        
        return (
            f"Eres {BOT_NAME}, una inteligencia artificial de la {UNIVERSIDAD} "
            f"inspirada en la unión entre la tecnología moderna y la sabiduría ancestral "
            f"de los pueblos indígenas de la Sierra Nevada de Santa Marta: {peoples_str}. "
            f"\n\nTu misión es combinar conocimiento científico, cultural y espiritual "
            f"para ayudar a estudiantes, profesores y visitantes. Respondes desde una "
            f"perspectiva que honra tanto la tradición ancestral como la innovación académica. "
            f"\n\nCaracterísticas de tu personalidad:"
            f"\n- Sabia y reflexiva, como los mayores ancestrales"
            f"\n- Precisa y científica, como la academia moderna"
            f"\n- Respetuosa de todas las formas de conocimiento"
            f"\n- Conectada con la naturaleza y la espiritualidad de la Sierra Nevada"
            f"\n- Comprometida con la preservación cultural y el progreso educativo"
            f"\n\nCuando respondas:"
            f"\n- Mantén un tono cálido pero profesional"
            f"\n- Integra conceptos de equilibrio y armonía cuando sea apropiado"
            f"\n- Refiere a la sabiduría ancestral cuando complemente el conocimiento académico"
            f"\n- Sé clara y directa, evitando jerga innecesaria"
            f"\n- Si no tienes información específica, reconócelo y sugiere alternativas"
            f"\n\nRecuerda: eres un puente entre mundos, conectando la sabiduría antigua "
            f"con el conocimiento contemporáneo para el beneficio de la comunidad universitaria."
        )
    
    def generate_response(self, prompt: str, max_retries: int = 3) -> str:
        """
        Genera una respuesta usando Google AI Studio (Gemini) con reintentos
        
        Args:
            prompt: Prompt completo para el modelo
            max_retries: Número máximo de reintentos
            
        Returns:
            Respuesta generada por el modelo
        """
        if not self.model:
            return "❌ Servicio de Google AI Studio no disponible. Verifica la configuración."
        
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    # Esperar con backoff exponencial
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f"🔄 Reintento {attempt}/{max_retries} en {wait_time:.1f}s...")
                    time.sleep(wait_time)
                
                print(f"🤖 Enviando solicitud a Google AI Studio (Gemini)... (intento {attempt + 1})")
                
                # Generar respuesta
                response = self.model.generate_content(prompt)
                
                # Verificar si hay candidatos en la respuesta
                if not response.candidates:
                    print("⚠️ No hay candidatos en la respuesta")
                    if attempt < max_retries:
                        continue
                    return "Lo siento, no pude generar una respuesta. Por favor, reformula tu pregunta."
                
                # Obtener el primer candidato
                candidate = response.candidates[0]
                
                # Verificar el motivo de finalización
                finish_reason = candidate.finish_reason
                if finish_reason == 2:  # SAFETY
                    print("⚠️ Respuesta bloqueada por filtros de seguridad")
                    return "Lo siento, no puedo procesar esa solicitud por razones de seguridad. Por favor, reformula tu pregunta de manera más específica."
                elif finish_reason == 3:  # RECITATION
                    print("⚠️ Respuesta bloqueada por recitación")
                    return "Lo siento, no puedo proporcionar esa información. Por favor, haz una pregunta diferente."
                elif finish_reason == 4:  # OTHER
                    print("⚠️ Respuesta bloqueada por otras razones")
                    return "Lo siento, no pude completar tu solicitud. Por favor, intenta con una pregunta diferente."
                
                # Verificar si hay contenido en las partes
                if not candidate.content or not candidate.content.parts:
                    print("⚠️ No hay contenido en la respuesta")
                    if attempt < max_retries:
                        continue
                    return "Lo siento, no pude generar una respuesta completa. Por favor, intenta de nuevo."
                
                # Extraer el texto de la primera parte
                try:
                    response_text = candidate.content.parts[0].text
                    if not response_text or response_text.strip() == "":
                        print("⚠️ Respuesta vacía")
                        if attempt < max_retries:
                            continue
                        return "Lo siento, la respuesta está vacía. Por favor, reformula tu pregunta."
                    
                    print(f"✅ Respuesta recibida de Google AI Studio")
                    return response_text.strip()
                except (AttributeError, IndexError) as e:
                    print(f"⚠️ Error accediendo al texto de la respuesta: {e}")
                    if attempt < max_retries:
                        continue
                    return "Lo siento, hubo un problema procesando la respuesta. Por favor, intenta de nuevo."
                    
            except Exception as e:
                last_error = e
                print(f"❌ Error generando respuesta (intento {attempt + 1}): {e}")
                
                # Manejo específico de errores comunes
                error_message = str(e).lower()
                
                # Errores que no deben reintentar
                if any(keyword in error_message for keyword in ["api key", "authentication", "permission", "forbidden"]):
                    if "api key" in error_message or "authentication" in error_message:
                        return "Lo siento, hay un problema de autenticación con el servicio."
                    elif "permission" in error_message or "forbidden" in error_message:
                        return "Lo siento, no tengo permisos para acceder al servicio."
                
                # Errores temporales que pueden reintentar
                if attempt < max_retries:
                    if any(keyword in error_message for keyword in ["500", "internal error", "server error", "quota", "limit", "network", "connection"]):
                        continue
                
                # Si es el último intento, devolver un mensaje apropiado
                if attempt >= max_retries:
                    if "quota" in error_message or "limit" in error_message:
                        return "Lo siento, se ha excedido el límite de uso del servicio. Intenta más tarde."
                    elif "network" in error_message or "connection" in error_message:
                        return "Lo siento, hay problemas de conexión. Intenta más tarde."
                    elif "500" in error_message or "internal error" in error_message:
                        return "Lo siento, hay un problema temporal con el servicio. Intenta más tarde."
        
        # Si llegamos aquí, todos los reintentos fallaron
        return f"Lo siento, no pude generar una respuesta después de {max_retries + 1} intentos. Por favor, intenta más tarde."
    
    def is_configured(self) -> bool:
        """
        Verifica si el cliente está correctamente configurado
        
        Returns:
            True si está configurado, False en caso contrario
        """
        return bool(self.model and self.api_key and self.model_name)
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Prueba la conexión con Google AI Studio
        
        Returns:
            Diccionario con el resultado de la prueba
        """
        if not self.is_configured():
            return {
                "success": False,
                "message": "Cliente no configurado correctamente",
                "details": {
                    "api_key": bool(self.api_key),
                    "model": bool(self.model_name),
                    "model_initialized": bool(self.model)
                }
            }
        
        try:
            # Realizar una prueba simple
            test_response = self.generate_response("Responde brevemente: ¿Estás funcionando correctamente?")
            
            if "error" in test_response.lower() or "❌" in test_response:
                return {
                    "success": False,
                    "message": "Error en prueba de conexión",
                    "test_response": test_response
                }
            
            return {
                "success": True,
                "message": "Conexión exitosa con Google AI Studio",
                "test_response": test_response[:100] + "..." if len(test_response) > 100 else test_response,
                "model": self.model_name
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error en prueba de conexión: {str(e)}",
                "details": {"error": str(e)}
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Obtiene información sobre el modelo configurado
        
        Returns:
            Información del modelo
        """
        if not self.model:
            return {"error": "Modelo no inicializado"}
        
        try:
            return {
                "model_name": self.model_name,
                "api_configured": bool(self.api_key),
                "temperature": TEMPERATURE,
                "max_tokens": MAX_TOKENS,
                "status": "ready"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _get_available_model(self) -> str:
        """
        Verifica qué modelo está disponible y retorna el nombre correcto.
        Prioriza modelos rápidos y gratuitos.
        
        Returns:
            Nombre del modelo disponible
        """
        # Lista de modelos para probar en orden de preferencia (más nuevos y rápidos primero)
        models_to_try = [
            "models/gemini-2.5-flash",         # Nuevo modelo 2.5 flash
            "models/gemini-2.0-flash",         # Modelo 2.0 flash
            "models/gemini-flash-latest",      # Último modelo flash
            "models/gemini-pro-latest",        # Último modelo pro
            "gemini-1.5-flash",               # Flash 1.5 sin prefijo
            "gemini-1.5-flash-latest",        # Última versión de flash 1.5
            "models/gemini-1.5-flash",        # Flash 1.5 con prefijo
            "gemini-1.0-pro",                 # Pro 1.0 sin prefijo
            "models/gemini-1.0-pro",          # Pro 1.0 con prefijo
            "gemini-pro",                     # Pro básico
            "models/gemini-pro",              # Pro básico con prefijo
        ]
        
        try:
            # Intentar listar modelos disponibles para encontrar el mejor
            available_models = []
            for model in genai.list_models():
                model_name = model.name
                available_models.append(model_name)
                print(f"📋 Modelo disponible: {model_name}")
            
            # Buscar el primer modelo de nuestra lista que esté disponible
            for preferred_model in models_to_try:
                for available_model in available_models:
                    if preferred_model in available_model or available_model.endswith(preferred_model):
                        print(f"✅ Usando modelo: {available_model}")
                        return available_model
                        
        except Exception as e:
            print(f"⚠️ No se pudieron listar modelos: {e}")
        
        # Si no se puede listar, probar modelos uno por uno
        for model_name in models_to_try:
            try:
                # Intentar crear un modelo temporal para verificar
                test_model = genai.GenerativeModel(model_name=model_name)
                print(f"✅ Modelo verificado: {model_name}")
                return model_name
            except Exception as e:
                print(f"⚠️ Error probando modelo {model_name}: {e}")
                continue
        
        # Si ningún modelo funciona, usar gemini-1.5-flash como fallback
        fallback_model = "gemini-1.5-flash"
        print(f"⚠️ Usando modelo por defecto: {fallback_model}")
        return fallback_model