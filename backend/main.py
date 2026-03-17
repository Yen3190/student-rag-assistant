from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import os
import shutil

from rag_engine import ask_question, db, reload_db
from ingest import ingest
from database import get_connection, init_db

app = FastAPI()

DATA_PATH = "data"


# ================= INIT DB =================
init_db()


# ================= MODEL =================
class Question(BaseModel):
    question: str


# ================= HOME =================
@app.get("/")
def home():
    return {"message": "Student RAG Assistant Running"}


# ================= CHAT =================
@app.post("/chat")
def chat(q: Question):

    result = ask_question(q.question)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO chats(question,answer) VALUES (?,?)",
        (q.question, result["answer"])
    )

    conn.commit()
    conn.close()

    return result


# ================= UPLOAD =================
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    # ✅ validate file
    if not file.filename.lower().endswith(".pdf"):
        return {"error": "Only PDF files are allowed"}

    file_path = os.path.join(DATA_PATH, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "File uploaded",
        "filename": file.filename,
        "note": "Call /rebuild to update AI"
    }


# ================= DELETE =================
@app.delete("/file/{filename}")
def delete_file(filename: str):

    path = os.path.join(DATA_PATH, filename)

    if not os.path.exists(path):
        return {"error": "File not found"}

    # ✅ FIX: xóa vector trong DB
    db.delete(where={"source": filename})

    # ✅ xóa file
    os.remove(path)

    return {"message": f"{filename} deleted"}


# ================= REBUILD =================
@app.post("/rebuild")
def rebuild_database():

    ingest()
    reload_db()

    return {"message": "Rebuilt + Reloaded"}


# ================= PDF LIST =================
@app.get("/pdfs")
def list_pdfs():

    pdf_files = [
        f for f in os.listdir(DATA_PATH)
        if f.lower().endswith(".pdf")
    ]

    return {
        "total_pdf": len(pdf_files),
        "pdf_files": pdf_files
    }


# ================= HISTORY =================
@app.get("/history")
def history():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT question, answer
    FROM chats
    ORDER BY id DESC
    LIMIT 50
    """)

    data = cursor.fetchall()

    conn.close()
    return data


# ================= ANALYTICS =================
@app.get("/analytics")
def analytics():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT question, COUNT(*) as total
    FROM chats
    GROUP BY question
    ORDER BY total DESC
    LIMIT 10
    """)

    data = cursor.fetchall()

    conn.close()
    return data


# ================= HEALTH =================
@app.get("/health")
def health():
    return {"status": "running"}