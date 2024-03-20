from fastapi import Depends, FastAPI, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy import MetaData, create_engine
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta


Base = declarative_base()

# Schemas


class CreateUser(BaseModel):
    id: int
    username: Optional[str]
    password: str
    role_id: int


class TodoBase(BaseModel):
    title: str
    description: str


class TodoCreate(TodoBase):
    pass


class TodoUpdate(TodoBase):
    completed: bool


class TodoInDB(TodoBase):
    id: int
    completed: bool
    created_at: datetime


# User Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(100))
    role_id = Column(Integer, ForeignKey("roles.id"))

    role = relationship("Role", back_populates="users")
    todos = relationship("Todo", back_populates="owner")


# Role Model
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)

    users = relationship("User", back_populates="role")


# Todo Model
class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    description = Column(String(255))
    done = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="todos")
    categories = relationship("Category", secondary="todo_categories", back_populates="todos")


# Category Model
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)

    todos = relationship("Todo", secondary="todo_categories", back_populates="categories")


app = FastAPI()

# Database connection settings
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root@localhost:3306/users"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
meta =MetaData()
conn = engine.connect()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Dependency for getting database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Password hashing helper
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Endpoint for user registration
@app.post("/register/", response_model=CreateUser)
def register_user(username: str, password: str, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(password)
    user = User(username=username, password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# Endpoint for user login
@app.post("/login/")
def login_user(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not pwd_context.verify(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    # Implement token generation (JWT) and return it
    return {"access_token": "fake_token", "token_type": "bearer"}


# Endpoint for creating a new todo
@app.post("/todos/", response_model=TodoBase)
def create_todo(todo_data: dict, db: Session = Depends(get_db)):
    todo = Todo(**todo_data)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


# Endpoint for updating a todo
@app.put("/todos/{todo_id}", response_model=TodoUpdate)
def update_todo(todo_id: int, todo_data: dict, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    for key, value in todo_data.items():
        setattr(todo, key, value)
    db.commit()
    db.refresh(todo)
    return todo


# Endpoint for deleting a todo
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted successfully"}
