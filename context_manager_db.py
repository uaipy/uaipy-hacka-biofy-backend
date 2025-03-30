from models import Message, Summary
from sqlalchemy.orm import Session
import openai
import tiktoken
from typing import List, Dict
from datetime import datetime

MODEL = "gpt-4o"
MAX_TOKENS = 120000
WINDOW_SIZE = 10
SUMMARIZE_THRESHOLD = 8000
enc = tiktoken.encoding_for_model(MODEL)

class ContextManagerDB:
    def __init__(self, db: Session):
        self.db = db

    def count_tokens(self, messages: List[str]) -> int:
        return sum(len(enc.encode(msg)) for msg in messages)

    def add_message(self, user_id: int, role: str, content: str):
        msg = Message(user_id=user_id, role=role, content=content)
        self.db.add(msg)
        self.db.commit()

        # Verifica se precisa resumir
        messages = self.get_history(user_id)
        if self.count_tokens([m.content for m in messages]) > SUMMARIZE_THRESHOLD:
            self._summarize_context(user_id, messages)

    def get_history(self, user_id: int) -> List[Message]:
        return self.db.query(Message).filter(Message.user_id == user_id).order_by(Message.timestamp).all()

    def get_context(self, user_id: int) -> List[Dict]:
        messages = self.get_history(user_id)
        print("messages: ", messages)
        window = messages[-WINDOW_SIZE:]
        summary = self.db.query(Summary).filter(Summary.user_id == user_id).first()
        print("summary: ", summary)

        msg_list = [{"role": msg.role, "content": msg.content} for msg in window]
        if summary:
            return [{"role": "system", "content": f"Resumo: {summary.content}"}] + msg_list
        return msg_list

    def _summarize_context(self, user_id: int, messages: List[Message]):
        text_to_summarize = "\n".join([f"{m.role}: {m.content}" for m in messages[:-WINDOW_SIZE]])
        print("text_to_smarize: ", summary)

        prompt = [
            {"role": "system", "content": "Resuma a conversa a seguir em até 5 linhas:"},
            {"role": "user", "content": text_to_summarize}
        ]

        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=prompt,
            temperature=0.5,
            max_tokens=300
        )

        summary = response['choices'][0]['message']['content']

        existing = self.db.query(Summary).filter(Summary.user_id == user_id).first()
        if existing:
            existing.content = summary
            existing.updated_at = datetime.utcnow()
        else:
            self.db.add(Summary(user_id=user_id, content=summary))
        self.db.commit()

        # Deleta mensagens antigas (exceto a janela)
        all_msgs = messages
        for msg in all_msgs[:-WINDOW_SIZE]:
            self.db.delete(msg)
        self.db.commit()
