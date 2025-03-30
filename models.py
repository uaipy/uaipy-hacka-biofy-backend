from sqlalchemy import JSON, Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    telefone = Column(String(20), nullable=False)
    details = Column(JSON, nullable=True)  # campo JSON para armazenar dados flexíveis

    messages = relationship("Message", back_populates="user", cascade="all, delete")
    summary = relationship("Summary", back_populates="user", uselist=False, cascade="all, delete")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # "user", "system" ou "assistant"
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="messages")

class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="summary")
