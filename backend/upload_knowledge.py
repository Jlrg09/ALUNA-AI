import requests
import sys
import os

def upload_document(api_url, filepath):
    filename = os.path.basename(filepath)
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    payload = {
        "filename": filename,
        "content": content
    }
    response = requests.post(api_url, json=payload)
    print("Respuesta:", response.json())

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python upload_knowledge.py http://localhost:5000/api/knowledge/upload archivo.txt")
        sys.exit(1)
    api_url = sys.argv[1]
    filepath = sys.argv[2]
    upload_document(api_url, filepath)