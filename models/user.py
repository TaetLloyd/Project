from pydantic import BaseModel
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from typing import Optional
from datetime import datetime, timedelta

from config.db import Base

class Todo(BaseModel):
    id: int
    name: Optional[str] 

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, index=True)


