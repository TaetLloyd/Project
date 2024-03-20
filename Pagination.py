from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from fastapi import BackgroundTasks

# Example database models
class User(BaseModel):
    id: int
    username: str
    email: str
    password: str
    role: str

class Todo(BaseModel):
    id: int
    title: str
    description: str
    status: str
    due_date: str
    category_id: Optional[int] = None
    assigned_to: Optional[int] = None

class Category(BaseModel):
    id: int
    name: str
    todos: List[int] = []


# FastAPI app
app = FastAPI()

# OAuth2 for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Authorization helper function
def get_current_user(token: str = Depends(oauth2_scheme)):
    # Example authentication logic
    if token != "validtoken":
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return users_db[1]  # Assuming user with ID 1 is authenticated


# Routes for managing user roles and permissions (admin only)
@app.post("/users/{user_id}/assign-role")
def assign_role(user_id: int, role: str, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = role
    return {"message": f"Role assigned to user {user_id}"}

# Routes for managing todos (authorization required)
@app.get("/todos/", response_model=List[Todo])
def get_todos(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        return [todo for todo in todos_db.values() if todo.assigned_to == current_user.id]
    return list(todos_db.values())

# Pagination and filtering example
@app.get("/todos/paginated/", response_model=List[Todo])
def get_paginated_todos(skip: int = 0, limit: int = 10):
    return list(todos_db.values())[skip : skip + limit]

# AsyncIO
def process_todo(todo_id: int):
    # Example async function
    todo = todos_db.get(todo_id)
    if todo:
        todo.status = "completed"

@app.post("/todos/{todo_id}/complete")
async def complete_todo(todo_id: int, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    background_tasks.add_task(process_todo, todo_id)
    return {"message": "Todo completion scheduled"}

# Request validation with Pydantic models
class TodoCreate(BaseModel):
    title: str
    description: str
    due_date: str


@app.post("/todos/", response_model=TodoCreate)
def create_todo(todo_data: TodoCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    todo_id = max(todos_db.keys()) + 1
    todo = Todo(id=todo_id, **todo_data.dict(), status="pending")
    todos_db[todo_id] = todo
    return todo
