from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
import logging
from huggingface_hub import InferenceClient

# Configuración
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(title="Daniel AI Assistant")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración
HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_NAME = os.getenv("HF_MODEL_NAME", "microsoft/Phi-4-mini-flash-reasoning")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN environment variable is not set")

client = InferenceClient(token=HF_TOKEN)

class Query(BaseModel):
    question: str

def build_prompt(question: str) -> str:
    return f"""
[INST] <<SYS>>
Eres Daniel Rada, experto en infraestructura cloud y ciberseguridad.
Responde de forma concisa en el mismo idioma de la pregunta.
<</SYS>>

Pregunta: {question}
[/INST]
"""

@app.post("/api/ask")
async def ask_question(query: Query):
    try:
        logger.info(f"Pregunta recibida: {query.question}")
        
        prompt = build_prompt(query.question)
        
        response = client.text_generation(
            prompt,
            model=MODEL_NAME,
            max_new_tokens=300,
            temperature=0.3,
            do_sample=True,
            return_full_text=False
        )
        
        logger.info(f"Respuesta generada: {response[:100]}...")
        return {"answer": response}
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"answer": "Lo siento, ocurrió un error al procesar tu pregunta"}

@app.get("/", response_class=HTMLResponse)
async def home():
    html_content = '''
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
            <div class="message bot">¡Hola! Soy Daniel Rada. ¿En qué puedo ayudarte?</div>
        </div>
        <div>
            <input type="text" id="message" placeholder="Escribe tu pregunta..." autocomplete="off">
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
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health():
    return {"status": "healthy", "model": MODEL_NAME}

# Handler para Vercel - IMPORTANTE
from mangum import Mangum
handler = Mangum(app)
