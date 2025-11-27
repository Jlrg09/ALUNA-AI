"""
Procesador de documentos simplificado sin dependencias problemáticas
"""
import os
import re
from typing import List, Dict

class SimpleDocumentProcessor:
    """Procesador básico de documentos"""
    
    def __init__(self, knowledge_dir: str = "documentos"):
        self.knowledge_dir = knowledge_dir
        self.supported_extensions = ['.txt']  # Solo texto por ahora
    
    def clean_text(self, text: str) -> str:
        """Limpia el texto de caracteres problemáticos"""
        # Remover caracteres especiales
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\n]', ' ', text)
        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text)
        # Remover líneas vacías
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    def read_text_file(self, filepath: str) -> str:
        """Lee un archivo de texto"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.clean_text(content)
        except Exception as e:
            print(f"Error leyendo {filepath}: {e}")
            return ""
    
    def process_documents(self) -> List[Dict]:
        """Procesa todos los documentos de texto"""
        documents = []
        
        if not os.path.exists(self.knowledge_dir):
            print(f"Directorio {self.knowledge_dir} no existe")
            return documents
        
        for filename in os.listdir(self.knowledge_dir):
            if not filename.endswith('.txt'):
                continue
            
            filepath = os.path.join(self.knowledge_dir, filename)
            content = self.read_text_file(filepath)
            
            if content and len(content) > 50:
                documents.append({
                    'filename': filename,
                    'content': content,
                    'size': len(content)
                })
                print(f"✅ Procesado: {filename} ({len(content)} caracteres)")
            else:
                print(f"⚠️ Archivo vacío o muy corto: {filename}")
        
        return documents
    
    def create_simple_search_index(self, documents: List[Dict]) -> Dict:
        """Crea un índice simple de búsqueda por palabras clave"""
        index = {}
        
        for i, doc in enumerate(documents):
            # Extraer palabras clave simples
            words = re.findall(r'\w+', doc['content'].lower())
            words = [w for w in words if len(w) > 3]  # Solo palabras de más de 3 caracteres
            
            for word in set(words):  # Usar set para evitar duplicados
                if word not in index:
                    index[word] = []
                index[word].append(i)
        
        return index
    
    def simple_search(self, query: str, documents: List[Dict], index: Dict) -> List[Dict]:
        """Búsqueda simple por palabras clave"""
        query_words = re.findall(r'\w+', query.lower())
        query_words = [w for w in query_words if len(w) > 3]
        
        if not query_words:
            return []
        
        # Contar coincidencias por documento
        doc_scores = {}
        for word in query_words:
            if word in index:
                for doc_idx in index[word]:
                    if doc_idx not in doc_scores:
                        doc_scores[doc_idx] = 0
                    doc_scores[doc_idx] += 1
        
        # Ordenar por puntuación
        if not doc_scores:
            return []
        
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Retornar los mejores documentos
        results = []
        for doc_idx, score in sorted_docs[:3]:  # Top 3
            doc = documents[doc_idx].copy()
            doc['score'] = score
            # Extracto relevante
            content = doc['content']
            preview = content[:300] + "..." if len(content) > 300 else content
            doc['preview'] = preview
            results.append(doc)
        
        return results

if __name__ == "__main__":
    # Ejecutar como módulo: python -m examples.simple_processor
    processor = SimpleDocumentProcessor()
    print("🚀 Procesando documentos...")
    documents = processor.process_documents()
    print(f"✅ Procesados {len(documents)} documentos")
