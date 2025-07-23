import requests
import sys

def chat(api_url, question):
    payload = {"question": question}
    response = requests.post(api_url, json=payload)
    print("Respuesta de Iguchat:", response.json()["answer"])

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python chat_console.py http://localhost:5000/api/chat \"Tu pregunta aquí\"")
        sys.exit(1)
    api_url = sys.argv[1]
    question = sys.argv[2]
    chat(api_url, question)