"""
FastAPI-based To-Do List API

This API allows users to register, log in, and manage their tasks securely.
Users can perform CRUD operations on their to-do list while ensuring authentication.

Dependencies:
- FastAPI
- Motor (MongoDB Async Driver)
- Passlib (Password Hashing)
- PyJWT (JSON Web Token Authentication)
- Pydantic (Data Validation)
"""

from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
import jwt
from bson import ObjectId
from jwt.exceptions import InvalidTokenError

# Environment Variables (Set these in your .env file)
MONGO_URI = "mongodb+srv://beingdillig:4CNlIcaPviSu0c72@todo.sbvg3.mongodb.net/?retryWrites=true&w=majority&appName=todo"
SECRET_KEY = "c19f5987d69e1ea701d4decd09bf8997c873340f3f8c15fe31395b057f5cf6fd"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()

# MongoDB Connection
client = AsyncIOMotorClient(MONGO_URI)
db = client.todo_app
users_collection = db.users
tasks_collection = db.tasks

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hashed version."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Generate a JWT access token with an optional expiration time."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

class User(BaseModel):
    """Schema for user registration and authentication."""
    username: str
    password: str

class Token(BaseModel):
    """Schema for JWT authentication response."""
    access_token: str
    token_type: str

class Task(BaseModel):
    """Schema for task creation and management."""
    title: str
    description: str | None = None
    completed: bool = False

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    """Retrieve the current authenticated user from the JWT token."""
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
    except InvalidTokenError:
        raise credentials_exception
    user = await users_collection.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return user

def to_do_serializer(todo_list: list) -> list:
    """Convert a single MongoDB task document or a list of documents to a JSON serializable format."""
    serialized_list = []
    for todo in todo_list:
        serialized_list.append({
            "_id": str(todo["_id"]),
            "title": todo["title"],
            "description": todo["description"],
            "completed": todo["completed"],
        })
    return serialized_list

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Authenticate user and return an access token."""
    user = await users_collection.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({"sub": user["username"]}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return Token(access_token=access_token, token_type="bearer")

@app.post("/register")
async def register(user: User):
    """Register a new user with hashed password."""
    existing_user = await users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed_password = get_password_hash(user.password)
    await users_collection.insert_one({"username": user.username, "password": hashed_password})
    return {"message": "User registered successfully"}

@app.post("/tasks/", response_model=Task)
async def create_task(task: Task, user: Annotated[dict, Depends(get_current_user)]):
    """Create a new task for the authenticated user."""
    task_dict = task.dict()
    task_dict["owner"] = user["username"]
    new_task = await tasks_collection.insert_one(task_dict)
    return {"id": str(new_task.inserted_id), **task_dict}

@app.get("/tasks/")
async def get_tasks(user: Annotated[dict, Depends(get_current_user)]):
    """Retrieve all tasks belonging to the authenticated user."""
    tasks = await tasks_collection.find({"owner": user["username"]}).to_list(length=100)
    return to_do_serializer(tasks)

@app.put("/tasks/{task_id}")
async def update_task(task_id: str, task: Task, user: Annotated[dict, Depends(get_current_user)]):
    """Update a task by its ID."""
    try:
        task_object_id = ObjectId(task_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid task ID")

    updated_task = await tasks_collection.update_one(
        {"_id": task_object_id, "owner": user["username"]}, {"$set": task.dict()}
    )
    if updated_task.modified_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task updated successfully"}

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str, user: Annotated[dict, Depends(get_current_user)]):
    """Delete a task by its ID."""
    try:
        task_object_id = ObjectId(task_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid task ID")

    deleted_task = await tasks_collection.delete_one({"_id": task_object_id, "owner": user["username"]})
    if deleted_task.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}
