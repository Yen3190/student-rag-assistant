from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = "chroma_db"

# ===== EMBEDDING =====
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ===== DB =====
db = Chroma(
    persist_directory=DB_PATH,
    embedding_function=embeddings
)

# 🔥 FIX: giảm context
retriever = db.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 5,          # 🔥 từ 30 -> 5
        "fetch_k": 20
    }
)

# 🔥 FIX: model nhẹ hơn
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)


def ask_question(query):
    try:
        docs = retriever.invoke(query)

        print("\n=== RETRIEVED DOCS ===")
        for d in docs:
            print(d.metadata.get("source"), "| page", d.metadata.get("page"))

        if not docs:
            return {
                "answer": "Tôi không tìm thấy thông tin.",
                "sources": []
            }

        # 🔥 FIX: chỉ lấy 5 docs
        docs = docs[:10]  

        # 🔥 FIX: cắt nội dung
        context = "\n\n".join([
            f"""
Nguồn: {d.metadata.get('source')}
Trang: {d.metadata.get('page')}

{d.page_content[:1000]}
"""
            for d in docs
        ])

        prompt = f"""
Bạn là trợ lý học vụ.

Trả lời NGẮN GỌN nhưng đầy đủ.
Nếu là bảng → tóm tắt lại.

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

    except Exception as e:
        print("ERROR:", e)
        return {
            "answer": "⚠️ Hệ thống đang quá tải hoặc hết token. Đợi 1 lúc rồi thử lại.",
            "sources": []
        }


def reload_db():
    global db, retriever

    db = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embeddings
    )

    # retriever = db.as_retriever(
    #     search_type="mmr",
    #     search_kwargs={
    #         "k": 5,
    #         "fetch_k": 20
    #     }
    # )
    retriever = db.as_retriever(
        search_type="similarity",   # 🔥 đổi mmr -> similarity
        search_kwargs={
            "k": 10                 # 🔥 tăng từ 5 -> 10
        }
    )