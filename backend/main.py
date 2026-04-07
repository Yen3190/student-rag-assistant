from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import shutil
from typing import List, Optional

# Import các hàm từ file nội bộ của em
from rag_engine import ask_question, db, reload_db
from ingest import ingest
from database import get_connection, init_db

app = FastAPI()

# ================= 1. CẤU HÌNH HỆ THỐNG =================

# Cho phép Frontend gọi API (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = "data"
init_db() # Khởi tạo SQLite

# Model dữ liệu để tránh lỗi 422
class QuestionRequest(BaseModel):
    question: str
    email: str 

class UserProfile(BaseModel):
    email: str
    fullname: str
    major: str = "Information Technology"
    university: str = "Van Lang University"

# ================= 2. API CHAT & LỊCH SỬ =================

@app.get("/health")
def health():
    return {"status": "running"}

@app.post("/chat")
def chat(q: QuestionRequest):
    try:
        # Gọi AI trả lời
        result = ask_question(q.question)
        
        # Lưu vào Database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chats(email, question, answer) VALUES (?,?,?)",
            (q.email, q.question, result["answer"])
        )
        conn.commit()
        conn.close()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
def history(email: str = Query(...)):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, question, answer FROM chats WHERE email = ? ORDER BY id DESC LIMIT 50", 
            (email,)
        )
        data = cursor.fetchall()
        conn.close()
        # Luôn trả về List để tránh lỗi .map() ở Frontend
        return [{"id": row[0], "question": row[1], "answer": row[2]} for row in data]
    except:
        return []

@app.delete("/history/{chat_id}")
def delete_chat(chat_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
    conn.commit()
    conn.close()
    return {"message": "Deleted"}

# ================= 3. QUẢN LÝ FILE & AI =================

@app.get("/pdfs")
def list_pdfs():
    if not os.path.exists(DATA_PATH): os.makedirs(DATA_PATH)
    pdf_files = [f for f in os.listdir(DATA_PATH) if f.lower().endswith(".pdf")]
    return {"total_pdf": len(pdf_files), "pdf_files": pdf_files}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not os.path.exists(DATA_PATH): os.makedirs(DATA_PATH)
    file_path = os.path.join(DATA_PATH, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": "Uploaded", "filename": file.filename}

@app.delete("/file/{filename}")
def delete_file(filename: str):
    path = os.path.join(DATA_PATH, filename)
    if os.path.exists(path):
        os.remove(path)
        return {"message": "Deleted"}
    return {"error": "Not found"}

@app.post("/rebuild")
def rebuild_database():
    ingest() # Đọc lại PDF
    reload_db() # Cập nhật Vector DB
    return {"message": "AI Rebuilt Successfully"}

# ================= 4. QUẢN LÝ NGƯỜI DÙNG (ADMIN) =================

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
    return {"message": "Success"}

@app.get("/admin/users")
def get_all_users():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT email, fullname, major, university FROM users")
        rows = cursor.fetchall()
        conn.close()
        return [{"email": r[0], "fullname": r[1], "major": r[2], "university": r[3]} for r in rows]
    except:
        return []

@app.delete("/admin/user/{email}")
def delete_user(email: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE email = ?", (email,))
    conn.commit()
    conn.close()
    return {"message": "User deleted"}

# ================= 5. PHỤC VỤ GIAO DIỆN (QUAN TRỌNG NHẤT) =================

# 1. Mount folder assets chứa file .js, .css đã build từ React
if os.path.exists("static/assets"):
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

# 2. Mount folder static nói chung
app.mount("/static", StaticFiles(directory="static"), name="static")

# 3. Trang chủ
@app.get("/")
async def serve_home():
    return FileResponse("static/index.html")

# 4. Xử lý Favicon
@app.get("/favicon.ico")
async def favicon():
    if os.path.exists("static/favicon.ico"):
        return FileResponse("static/favicon.ico")
    return FileResponse("static/index.html")

# 5. Cấu hình Catch-all Route (Fix lỗi Refresh trang 404)
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # Nếu là file có thật (ảnh, js, css) thì trả về file đó
    file_path = os.path.join("static", full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Nếu không phải file (ví dụ gõ /history) thì trả về index.html cho React điều hướng
    return FileResponse("static/index.html")