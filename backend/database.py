import sqlite3

DB_PATH = "chat_history.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        question TEXT,
        answer TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        fullname TEXT,
        major TEXT,
        university TEXT DEFAULT 'Van Lang University'
    )
    """)

    cursor.execute("INSERT OR IGNORE INTO users (email, fullname, major) VALUES (?,?,?)", 
                   ("thunguyen465933@gmail.com", "Anh Thư", "Information Technology"))

    conn.commit()
    conn.close()