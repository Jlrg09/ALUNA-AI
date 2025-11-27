"""
Script de prueba para verificar que las rutas de los archivos PKL están correctas
"""
import os
from config import EMBEDDINGS_FILE, MEMORY_FILE

print("=" * 60)
print("🔍 Verificación de Rutas de Archivos PKL")
print("=" * 60)

print(f"\n📁 EMBEDDINGS_FILE:")
print(f"   Ruta configurada: {EMBEDDINGS_FILE}")
print(f"   Existe: {'✅ Sí' if os.path.exists(EMBEDDINGS_FILE) else '❌ No'}")
if os.path.exists(EMBEDDINGS_FILE):
    print(f"   Tamaño: {os.path.getsize(EMBEDDINGS_FILE):,} bytes")

print(f"\n📁 MEMORY_FILE:")
print(f"   Ruta configurada: {MEMORY_FILE}")
print(f"   Existe: {'✅ Sí' if os.path.exists(MEMORY_FILE) else '❌ No'}")
if os.path.exists(MEMORY_FILE):
    print(f"   Tamaño: {os.path.getsize(MEMORY_FILE):,} bytes")

print(f"\n📂 Contenido de la carpeta data/:")
data_dir = os.path.dirname(EMBEDDINGS_FILE)
if os.path.exists(data_dir):
    files = os.listdir(data_dir)
    for f in files:
        full_path = os.path.join(data_dir, f)
        if os.path.isfile(full_path):
            size = os.path.getsize(full_path)
            print(f"   - {f} ({size:,} bytes)")
else:
    print(f"   ⚠️ El directorio '{data_dir}' no existe")

print(f"\n🔍 Archivos PKL en raíz:")
root_pkl_files = [f for f in os.listdir('.') if f.endswith('.pkl')]
if root_pkl_files:
    print(f"   ⚠️ Se encontraron {len(root_pkl_files)} archivo(s) PKL en raíz:")
    for f in root_pkl_files:
        print(f"      - {f}")
else:
    print(f"   ✅ No hay archivos PKL en la raíz")

print("\n" + "=" * 60)
print("✅ Verificación completada")
print("=" * 60)
