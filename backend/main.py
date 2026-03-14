from fastapi import FastAPI, UploadFile, File, BackgroundTasks
import shutil
import os
from dotenv import load_dotenv

load_dotenv(".env.local")

DATA_PATH = os.getenv("DATA_PATH", "data")
DB_PATH = os.getenv("DB_PATH", "chroma_db")

if not os.path.exists(DATA_PATH):
    os.makedirs(DATA_PATH)

from ingest import ingest
from pydantic import BaseModel
from rag_engine import ask_question
from chat_history import get_history
from rag_engine import db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    question: str


@app.get("/")
def home():
    return {"message": "Student RAG Assistant Running"}


@app.post("/chat")
def chat(q: Question):

    result = ask_question(q.question)

    return result


@app.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):

    file_path = os.path.join(DATA_PATH, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    background_tasks.add_task(ingest)

    return {"message": f"{file.filename} uploaded and indexed successfully"}


@app.get("/history")
def history():
    return get_history()


@app.get("/files")
def list_files():

    files = os.listdir(DATA_PATH)

    return {"files": files}


@app.delete("/delete/{filename}")
def delete_file(filename: str):

    path = os.path.join(DATA_PATH, filename)

    if os.path.exists(path):

        os.remove(path)

        db.delete(where={"source": filename})

        return {"message": "file deleted and vectors removed"}

    return {"error": "file not found"}


@app.post("/reindex")
def rebuild():

    ingest()

    return {"message": "database rebuilt"}


@app.get("/health")
def health():

    return {
        "status": "ok",
        "service": "student-rag-assistant-backend"
    }