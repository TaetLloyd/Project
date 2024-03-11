from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from tokenize import Token
from typing import List, Union
from models.user import Todo, User
from fastapi import APIRouter
from config.db import conn,SessionLocal
from schemas.user import TodoCreate, TodoInDB, TodoUpdate, TokenData, UserCreate, UserInDB
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.ext.declarative import declarative_base
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import uvicorn

SECRET_KEY = "secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# FastAPI app
app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create user
def create_user(db: Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Authenticate user
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

# Create access token
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Get current user
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
def get_current_user(token:str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    return token_data

# OAuth2 password bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Authenticate user and create access token
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Register user
@app.post("/register", response_model=UserInDB)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = create_user(db, user)
    return db_user

# Get all todos
@app.get("/todos/", response_model=List[TodoInDB])
async def read_todos(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    return db.query(Todo).filter(Todo.user_id == current_user.id).offset(skip).limit(limit).all()

# Create todo
@app.post("/todos/", response_model=TodoInDB)
async def create_todo(todo: TodoCreate, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    db_todo = Todo(**todo.dict(), user_id=current_user.id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

# Update todo
@app.put("/todos/{todo_id}", response_model=TodoInDB)
async def update_todo(todo_id: int, todo: TodoUpdate, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == current_user.id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    for var, value in vars(todo).items():
        setattr(db_todo, var, value) if value else None
    db.commit()
    db.refresh(db_todo)
    return db_todo

# Mark todo as completed
@app.put("/todos/{todo_id}/complete", response_model=TodoInDB)
async def complete_todo(todo_id: int, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == current_user.id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db_todo.completed = True
    db.commit()
    db.refresh(db_todo)
    return db_todo

if __name__ == "__main__":
   uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
