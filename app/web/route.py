from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# HTML simple para la interfaz
HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Daniel AI Assistant</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .chat-container { border: 1px solid #ddd; padding: 20px; border-radius: 10px; }
        .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .user { background: #e3f2fd; }
        .bot { background: #f5f5f5; }
        input, button { padding: 10px; margin: 5px; }
        input { width: 70%; }
    </style>
</head>
<body>
    <h1>🤖 Daniel AI Assistant</h1>
    <div class="chat-container">
        <div id="chat"></div>
        <input type="text" id="message" placeholder="Escribe tu pregunta sobre cloud o ciberseguridad...">
        <button onclick="sendMessage()">Enviar</button>
    </div>

    <script>
        async function sendMessage() {
            const messageInput = document.getElementById('message');
            const message = messageInput.value;
            if (!message) return;
            
            const chat = document.getElementById('chat');
            
            // Agregar mensaje del usuario
            chat.innerHTML += `<div class="message user"><strong>Tú:</strong> ${message}</div>`;
            messageInput.value = '';
            
            try {
                const response = await fetch('/api/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question: message })
                });
                
                const data = await response.json();
                chat.innerHTML += `<div class="message bot"><strong>AI:</strong> ${data.answer}</div>`;
                
                // Scroll al final
                chat.scrollTop = chat.scrollHeight;
            } catch (error) {
                chat.innerHTML += `<div class="message bot" style="color: red;">Error: No se pudo conectar con el servidor</div>`;
            }
        }
        
        // Permitir enviar con Enter
        document.getElementById('message').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return HTML

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_input = request.json.get('message')
        # Llamar a la API
        response = requests.post(
            "/api/ask",
            json={"question": user_input, "session_id": "web"}
        )
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"answer": f"Error: {str(e)}"})

# Handler para Vercel
def handler(request):
    return app(request)
