"""
Script de prueba para el servicio de visión computacional
Prueba las funcionalidades principales sin necesidad de subir archivos
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.vision_service import VisionService
from PIL import Image
import numpy as np
import io


def create_test_image():
    """Crea una imagen de prueba simple"""
    # Crear una imagen con patrones geométricos simples
    img = Image.new('RGB', (200, 200), color='white')
    pixels = img.load()
    
    # Agregar algunos patrones de colores
    for i in range(200):
        for j in range(200):
            if i < 100:
                if j < 100:
                    pixels[i, j] = (255, 0, 0)  # Rojo
                else:
                    pixels[i, j] = (0, 255, 0)  # Verde
            else:
                if j < 100:
                    pixels[i, j] = (0, 0, 255)  # Azul
                else:
                    pixels[i, j] = (255, 255, 0)  # Amarillo
    
    return img


def test_vision_service():
    """Prueba principal del servicio de visión"""
    print("🧪 Iniciando pruebas del servicio de visión...")
    print("=" * 50)
    
    # Inicializar servicio
    try:
        vision_service = VisionService()
        print("✅ Servicio de visión inicializado")
    except Exception as e:
        print(f"❌ Error inicializando servicio: {e}")
        return False
    
    # Verificar estado del servicio
    print("\n📊 Estado del servicio:")
    status = vision_service.get_service_status()
    for component, available in status.items():
        emoji = "✅" if available else "❌"
        print(f"  {emoji} {component}: {available}")
    
    if not vision_service.is_available():
        print("\n⚠️ Servicio de visión no completamente disponible")
        print("   Esto es normal si no tienes los modelos descargados")
        print("   Las funcionalidades básicas seguirán funcionando")
    
    # Probar análisis de imagen
    print("\n🖼️ Probando análisis de imagen...")
    try:
        # Crear imagen de prueba
        test_image = create_test_image()
        
        # Convertir a bytes
        img_byte_arr = io.BytesIO()
        test_image.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
        
        # Analizar imagen
        result = vision_service.analyze_image_from_bytes(img_bytes, "test_image.png")
        
        if "error" in result:
            print(f"❌ Error en análisis: {result['error']}")
        else:
            print("✅ Análisis completado exitosamente")
            print(f"   Descripción: {result.get('description', 'N/A')}")
            print(f"   Objetos detectados: {len(result.get('objects_detected', []))}")
            print(f"   Objetos culturales: {len(result.get('cultural_objects', []))}")
            print(f"   Colores dominantes: {len(result.get('dominant_colors', []))}")
            print(f"   Confianza general: {result.get('confidence_score', 0)}")
            
            if result.get('cultural_objects'):
                print("   🏺 Objetos culturales detectados:")
                for obj in result['cultural_objects']:
                    print(f"     - {obj['name']} ({obj['culture']}) - {obj['confidence']:.2%}")
    
    except Exception as e:
        print(f"❌ Error en análisis de imagen: {e}")
    
    # Probar base de datos de objetos culturales
    print("\n🏛️ Probando base de datos de objetos culturales...")
    try:
        cultural_objects = vision_service.get_cultural_objects_info()
        print(f"✅ Base de datos cargada con {len(cultural_objects)} objetos:")
        for obj_id, obj_info in cultural_objects.items():
            print(f"   - {obj_info['name']} ({obj_info['culture']})")
    except Exception as e:
        print(f"❌ Error cargando base de datos: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Pruebas del servicio de visión completadas")
    return True


def test_specific_cultural_keywords():
    """Prueba detección de palabras clave específicas"""
    print("\n🔍 Probando detección de palabras clave...")
    
    vision_service = VisionService()
    
    # Simular descripciones con palabras clave culturales
    test_descriptions = [
        "a colorful woven bag with geometric patterns",
        "traditional brown gourd container vessel",
        "white traditional clothing garment robe",
        "colorful beads necklace with geometric patterns",
        "traditional hat made of straw"
    ]
    
    for description in test_descriptions:
        # Simular objetos detectados vacíos
        objects_detected = []
        
        cultural_matches = vision_service._identify_cultural_objects(description, objects_detected)
        
        print(f"   Descripción: '{description}'")
        if cultural_matches:
            for match in cultural_matches:
                print(f"     -> {match['name']} ({match['confidence']:.2%})")
        else:
            print("     -> No se detectaron objetos culturales")
        print()


if __name__ == "__main__":
    success = test_vision_service()
    
    if success:
        test_specific_cultural_keywords()
    
    print("\n💡 Para usar el servicio:")
    print("   1. Instala las dependencias: pip install -r requirements_vision.txt")
    print("   2. Inicia el servidor: python app.py")
    print("   3. Prueba los endpoints:")
    print("      - POST /api/vision/analyze (subir imagen)")
    print("      - GET /api/vision/status (estado del servicio)")
    print("      - GET /api/vision/cultural-objects (objetos en base de datos)")
    print("      - POST /api/vision/test (prueba rápida)")