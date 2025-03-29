from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from context_manager_db import ContextManagerDB
from database import SessionLocal, engine
import models
import openai
import os

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
