from fastapi import FastAPI, status as STATUS, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from database import SessionLocal, engine
import models
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import Security
import time

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:3000",
    "localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

# --- Auth Setup ---
SECRET_KEY = "supersecretkey"  # In production, use env var
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

fake_users_db = {
    "testuser": {
        "username": "testuser",
        "hashed_password": pwd_context.hash("testpass")
    }
}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str):
    user = fake_users_db.get(username)
    if user:
        return user
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: int = None):
    to_encode = data.copy()
    expire = time.time() + (expires_delta or ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Security(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=STATUS.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Task(BaseModel):
    id:int   
    title:str 
    status:bool  
    class Config:
        orm_mode = True

class TaskCreate(BaseModel):
    title: str

@app.post("/register")
def register(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = pwd_context.hash(form_data.password)
    fake_users_db[form_data.username] = {
        "username": form_data.username,
        "hashed_password": hashed_password
    }
    return {"msg": "User registered"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Monitoring ---
Instrumentator().instrument(app).expose(app)

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# --- Secure all task endpoints ---
@app.get('/tasks', response_model = List[Task], status_code = 200)
async def get_all_tasks(db: SessionLocal = Depends(get_db), user: dict = Depends(get_current_user)):
    tasks = db.query(models.Task).all() 
    return tasks

@app.get('/task/{task_id}', response_model = Task, status_code = STATUS.HTTP_200_OK)
async def get_task(task_id: int, db: SessionLocal = Depends(get_db), user: dict = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=STATUS.HTTP_404_NOT_FOUND,detail="Resource Not Found")
    return task

@app.get('/tasks/{task_status}', response_model = List[Task], status_code = STATUS.HTTP_200_OK)
async def get_task_by_status(task_status:int, db: SessionLocal = Depends(get_db), user: dict = Depends(get_current_user)):
    tasks = db.query(models.Task).filter(models.Task.status==task_status).all()
    if tasks is None:
        raise HTTPException(status_code=STATUS.HTTP_404_NOT_FOUND,detail="Resource Not Found")
    return tasks

@app.post('/tasks', response_model = Task, status_code = STATUS.HTTP_201_CREATED)
async def create_an_task(task:TaskCreate, db: SessionLocal = Depends(get_db), user: dict = Depends(get_current_user)):
    new_task = models.Task(title = task.title)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.put('/task/{task_id}', response_model = Task, status_code = STATUS.HTTP_200_OK)
async def update_an_task(task_id:int, task:Task, db: SessionLocal = Depends(get_db), user: dict = Depends(get_current_user)):
    task_to_update = db.query(models.Task).filter(models.Task.id==task_id).first()
    if task_to_update is None:
        raise HTTPException(
            status_code = STATUS.HTTP_404_NOT_FOUND,
            detail = "Resource Not Found" )
    task_to_update.title = task.title
    task_to_update.status = task.status
    db.commit()
    db.refresh(task_to_update)
    return task_to_update

@app.delete('/task/{task_id}')
async def delete_item(task_id:int, db: SessionLocal = Depends(get_db), user: dict = Depends(get_current_user)):
    task_to_delete = db.query(models.Task).filter(models.Task.id==task_id).first()
    if task_to_delete is None:
        raise HTTPException(status_code=STATUS.HTTP_404_NOT_FOUND, detail="Resource Not Found")
    db.delete(task_to_delete)
    db.commit()
    return task_to_delete