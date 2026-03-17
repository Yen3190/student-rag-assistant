from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = "chroma_db"

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = Chroma(
    persist_directory=DB_PATH,
    embedding_function=embeddings
)

retriever = db.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 30,      # 🔥 tăng context
        "fetch_k": 80
    }
)

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)


def ask_question(query):

    docs = retriever.invoke(query)

    if not docs:
        return {
            "answer": "Tôi không tìm thấy thông tin trong tài liệu.",
            "sources": []
        }

    context = "\n\n".join([
        f"""
Nguồn: {d.metadata.get('source')}
Trang: {d.metadata.get('page')}

{d.page_content}
"""
        for d in docs
    ])

    prompt = f"""
Bạn là trợ lý học vụ.

Hãy trả lời ĐẦY ĐỦ, KHÔNG bỏ sót thông tin.
Nếu dữ liệu là bảng → phải tổng hợp toàn bộ.

Tài liệu:
{context}

Câu hỏi:
{query}
"""

    response = llm.invoke(prompt)

    sources = list({
        f"{d.metadata.get('source')} (page {d.metadata.get('page')})"
        for d in docs
    })

    return {
        "answer": response.content,
        "sources": sources
    }


def reload_db():
    global db, retriever

    db = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embeddings
    )

    retriever = db.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 30,
            "fetch_k": 80
        }
    )