from flask import Flask, request, jsonify
import os
import logging
from huggingface_hub import InferenceClient

app = Flask(__name__)

# Configuración
HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_NAME = os.getenv("HF_MODEL_NAME", "microsoft/Phi-4-mini-flash-reasoning")

if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN no configurado")

client = InferenceClient(token=HF_TOKEN)

def build_prompt(question):
    return f"""
[INST] <<SYS>>
Eres Daniel Rada, experto en infraestructura cloud y ciberseguridad.
Responde de forma concisa en el mismo idioma de la pregunta.
<</SYS>>

Pregunta: {question}
[/INST]
"""

@app.route('/')
def home():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Daniel AI Assistant</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .chat-container {
            height: 400px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 5px;
        }
        .message {
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
        }
        .user {
            background: #e3f2fd;
            margin-left: 20%;
        }
        .bot {
            background: #f5f5f5;
            margin-right: 20%;
        }
        input {
            width: 70%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-right: 10px;
        }
        button {
            padding: 10px 20px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Daniel AI Assistant</h1>
        <div class="chat-container" id="chat">
            <div class="message bot"><strong>AI:</strong> ¡Hola! Soy Daniel Rada. ¿En qué puedo ayudarte?</div>
        </div>
        <div>
            <input type="text" id="message" placeholder="Escribe tu pregunta sobre cloud o ciberseguridad..." autocomplete="off">
            <button onclick="sendMessage()">Enviar</button>
        </div>
    </div>

    <script>
        async function sendMessage() {
            const messageInput = document.getElementById('message');
            const message = messageInput.value.trim();
            if (!message) return;

            const chat = document.getElementById('chat');
            
            // Agregar mensaje del usuario
            chat.innerHTML += `<div class="message user"><strong>Tú:</strong> ${message}</div>`;
            messageInput.value = '';

            try {
                const response = await fetch('/api/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        question: message
                    })
                });
                
                const data = await response.json();
                chat.innerHTML += `<div class="message bot"><strong>AI:</strong> ${data.answer}</div>`;
                
                // Scroll al final
                chat.scrollTop = chat.scrollHeight;
            } catch (error) {
                chat.innerHTML += `<div class="message bot" style="color: red;">Error de conexión</div>`;
            }
        }

        // Enviar con Enter
        document.getElementById('message').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
'''

@app.route('/api/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        prompt = build_prompt(question)
        response = client.text_generation(
            prompt,
            model=MODEL_NAME,
            max_new_tokens=300,
            temperature=0.3,
            do_sample=True
        )
        
        return jsonify({'answer': response})
    except Exception as e:
        return jsonify({'answer': f'Error: {str(e)}'})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'model': MODEL_NAME})

# Handler para Vercel - ESTA ES LA CLAVE
def handler(request):
    return app(request)
