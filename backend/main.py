from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil

from rag_engine import ask_question, db, reload_db
from ingest import ingest
from database import get_connection, init_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = "data"

# ================= 1. KHỞI TẠO =================
init_db()

# Model dữ liệu
class Question(BaseModel):
    question: str
    email: str 

class UserProfile(BaseModel):
    email: str
    fullname: str
    major: str = "Information Technology"
    university: str = "Van Lang University"

# ================= 2. TRANG CHỦ & KIỂM TRA =================
@app.get("/")
def home():
    return {"message": "Student RAG Assistant Running"}

@app.get("/health")
def health():
    return {"status": "running"}

# ================= 3. XỬ LÝ CHAT & LỊCH SỬ =================

@app.post("/chat")
def chat(q: Question):
    result = ask_question(q.question)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chats(email, question, answer) VALUES (?,?,?)",
        (q.email, q.question, result["answer"])
    )
    conn.commit()
    conn.close()
    return result

@app.get("/history")
def history(email: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, question, answer FROM chats WHERE email = ? ORDER BY id DESC LIMIT 50", 
        (email,)
    )
    data = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "question": row[1], "answer": row[2]} for row in data]

# API xóa tin nhắn trong History (Dùng cho History.jsx)
@app.delete("/history/{chat_id}")
def delete_chat(chat_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
    conn.commit()
    conn.close()
    return {"message": "Deleted chat successfully"}

# ================= 4. QUẢN LÝ TÀI LIỆU (PDF) =================

@app.get("/pdfs")
def list_pdfs():
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
        return {"total_pdf": 0, "pdf_files": []}
    pdf_files = [f for f in os.listdir(DATA_PATH) if f.lower().endswith(".pdf")]
    return {"total_pdf": len(pdf_files), "pdf_files": pdf_files}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        return {"error": "Only PDF files are allowed"}
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
    file_path = os.path.join(DATA_PATH, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": "File uploaded", "filename": file.filename}

@app.delete("/file/{filename}")
def delete_file(filename: str):
    path = os.path.join(DATA_PATH, filename)
    if os.path.exists(path):
        os.remove(path)
        return {"message": f"{filename} deleted"}
    return {"error": "File not found"}

# ================= 5. HỆ THỐNG AI (REBUILD) =================

@app.post("/rebuild")
def rebuild_database():
    ingest()
    reload_db()
    return {"message": "Rebuilt + Reloaded"}

# ================= 6. QUẢN LÝ NGƯỜI DÙNG =================

# API: Lưu/Cập nhật thông tin khi đăng nhập (BẮT BUỘC PHẢI CÓ để lưu user mới)
@app.post("/user/update_profile")
def update_profile(profile: UserProfile):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO users (email, fullname, major, university)
        VALUES (?, ?, ?, ?)
    """, (profile.email, profile.fullname, profile.major, profile.university))
    conn.commit()
    conn.close()
    return {"message": "Profile updated successfully"}

# API: Lấy danh sách cho trang Quản lý Admin (Dùng cho UserManagement.jsx)
@app.get("/admin/users")
def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email, fullname, major, university FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"email": r[0], "fullname": r[1], "major": r[2], "university": r[3]} 
        for r in rows
    ]

# API: Xóa tài khoản (Dùng cho UserManagement.jsx)
@app.delete("/admin/user/{email}")
def delete_user(email: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE email = ?", (email,))
    cursor.execute("DELETE FROM chats WHERE email = ?", (email,))
    conn.commit()
    conn.close()
    return {"message": f"User {email} deleted"}

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
    return [{"question": r[0], "count": r[1]} for r in data]