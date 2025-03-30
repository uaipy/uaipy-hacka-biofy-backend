from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from context_manager_db import ContextManagerDB
from database import SessionLocal, engine
import models
import openai
import os
import requests

from resposta_handler import montar_resposta
import user_schema
import user_service


load_dotenv() 

# Z-API DATA
INSTANCE_ID = os.getenv("INSTANCE_ID")
TOKEN = os.getenv("TOKEN")
API_KEY = os.getenv("OPENAI_API_KEY")
CLIENT_TOKEN= os.getenv("CLIENT_TOKEN")
ZAPI_URL = f"https://api.z-api.io/instances/{INSTANCE_ID}/token/{TOKEN}"

# OpenAI DATA
openai.api_key = API_KEY
openai.project = os.getenv("API_PROJECT")
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos
    allow_headers=["*"],  # Permite todos os headers
)

# Request/response
class ChatRequest(BaseModel):
    user_id: int
    message: str

class ChatResponse(BaseModel):
    response: str

class MessageText(BaseModel):
    message: str

class MensagemBody(BaseModel):
    numero: str
    text: MessageText

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
def enviar_mensagem(body: MensagemBody, db: Session = Depends(get_db)):
    print(f"📥 Nova mensagem de {body}.")
    phone = body.numero

    headers = {
        "Client-Token": CLIENT_TOKEN
    }        

    db_user = user_service.get_user_by_telefone(db, phone)
    if db_user is None:
        try:
            user_response= {
            "phone": phone,
            "message": "Olá, recebemos sua mensagem, mas percebemos que infelizmente voce ainda nao tem cadastro. Por favor, va ao nosso site e se cadastre."
            }
            response = requests.post(f"{ZAPI_URL}/send-messages", json=user_response, headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[ERRO] Falha ao enviar mensagem para ZAPI: {e}")
            raise HTTPException(status_code=502, detail="Erro ao enviar mensagem para o provedor externo.")

        return JSONResponse(content={"status": response.json()})

    # Convertendo o objeto Pydantic para dicionário
    body_dict = body.model_dump()
    user_response = montar_resposta(db_user.name, phone, body_dict, API_KEY)
    
    try:
        response = requests.post(f"{ZAPI_URL}/send-messages", json=user_response, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERRO] Falha ao enviar mensagem para ZAPI: {e}")
        raise HTTPException(status_code=502, detail="Erro ao enviar mensagem para o provedor externo.")

    return JSONResponse(content={"status": response.json()})

# Webhook para receber mensagens dos usuários
@app.post("/webhook/zapi")
async def receber_mensagem(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
    except Exception as e:
        print(f"[ERRO] Falha ao processar JSON: {e}")
        raise HTTPException(status_code=400, detail="Corpo da requisição inválido.")

    phone = body.get("phone")
    
    if not phone:
        print("[ERRO] Número de telefone ausente no payload.")
        raise HTTPException(status_code=400, detail="Número de telefone ausente.")
    
    headers = {
        "Client-Token": CLIENT_TOKEN
    }
    
    db_user = user_service.get_user_by_telefone(db, phone)
    if db_user is None:
        try:
            user_response= {
            "phone": phone,
            "message": "Olá, recebemos sua mensagem, mas percebemos que infelizmente voce ainda nao tem cadastro. Por favor, va ao nosso site e se cadastre."
            }
            response = requests.post(f"{ZAPI_URL}/send-messages", json=user_response, headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[ERRO] Falha ao enviar mensagem para ZAPI: {e}")
            raise HTTPException(status_code=502, detail="Erro ao enviar mensagem para o provedor externo.")

        return JSONResponse(content={"status": response.json()})

    print(f"📥 Nova mensagem de {db_user.name} ({phone}).")
    print("MENSAGEM PURA:", body)

    user_response = montar_resposta(db_user.name, phone, body, API_KEY)

    try:
        response = requests.post(f"{ZAPI_URL}/send-messages", json=user_response, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERRO] Falha ao enviar mensagem para ZAPI: {e}")
        raise HTTPException(status_code=502, detail="Erro ao enviar mensagem para o provedor externo.")

    return JSONResponse(content={"status": response.json()})


# USER ROUTES

@app.post("/user", response_model=user_schema.UserOut)
def create_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, user)

@app.get("/user/{user_id}", response_model=user_schema.UserOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_service.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/user", response_model=list[user_schema.UserOut])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return user_service.get_users(db, skip, limit)

@app.put("/user/{user_id}", response_model=user_schema.UserOut)
def update_user(user_id: int, user: user_schema.UserUpdate, db: Session = Depends(get_db)):
    db_user = user_service.update_user(db, user_id, user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.delete("/user/{user_id}", response_model=user_schema.UserOut)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_service.delete_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/user/by-telefone/{telefone}", response_model=user_schema.UserOut)
def read_user_by_telefone(telefone: str, db: Session = Depends(get_db)):
    db_user = user_service.get_user_by_telefone(db, telefone)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
