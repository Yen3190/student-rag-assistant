from fastapi import FastAPI, UploadFile, File
import shutil
import os
from ingest import ingest
from pydantic import BaseModel
from rag_engine import ask_question
from chat_history import get_history

app = FastAPI()

DATA_PATH = "data"

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
async def upload_file(file: UploadFile = File(...)):

    file_path = os.path.join(DATA_PATH, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    ingest()

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
        return {"message": "file deleted"}

    return {"error": "file not found"}


@app.post("/reindex")
def rebuild():

    ingest()

    return {"message": "database rebuilt"}