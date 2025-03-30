from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from context_manager_db import ContextManagerDB
from database import SessionLocal, engine
import models
import openai
import os
import requests

# OpenAI DATA
openai.api_key = os.getenv("OPENAI_API_KEY") or "" #ADD THE KEY HERE - DO NOT COMMIT SECRETS
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Request/response
class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    response: str

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    context = ContextManagerDB(db)
    context.add_message(request.user_id, "user", request.message)

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=context.get_context(request.user_id),
            temperature=0.7,
            max_tokens=1000
        )

        reply = completion['choices'][0]['message']['content']
        context.add_message(request.user_id, "assistant", reply)
        for msg in context.get_history(request.user_id):
            print(f"Message content: {msg.content}, Sender: {msg.role}")

        return ChatResponse(response=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Modelo para enviar mensagem
class Mensagem(BaseModel):
    numero: str  # Ex: "5591999999999"
    mensagem: str

# Endpoint para envio manual de mensagens
@app.post("/enviar")
def enviar_mensagem(msg: Mensagem):
    print(msg)
    payload = {
        "phone": msg.numero,
        "message": msg.mensagem
    }
    headers = {
        "Client-Token": CLIENT_TOKEN
    }
    response = requests.post(f"{ZAPI_URL}/send-messages", json=payload, headers=headers)
    print(response.json())
    return response.json()

# Webhook para receber mensagens dos usuários
@app.post("/webhook/zapi")
async def receber_mensagem(request: Request):
    body = await request.json()
    print(body)
    if body.get("status") == "RECEIVED":
        message = body["text"]["message"]
        sender = body.get("senderName")
        remetente = body.get("phone")

        print(f"📥 Nova mensagem de {sender} ({remetente}): {message}")

        # Resposta automática
        user_response = {
            "phone": remetente,
            "message": f"Olá {sender}, recebi sua mensagem: \"{message}\". Essa é uma mensagem da UAIGRO para voce se sentir mais confiante."
        }
        headers = {
            "Client-Token": CLIENT_TOKEN
        }
        api_response = requests.post(f"{ZAPI_URL}/send-messages", json=user_response, headers=headers)

    return {"status": api_response.json()}