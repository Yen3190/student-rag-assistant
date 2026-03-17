from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = "chroma_db"

# ===== EMBEDDING =====
embeddings = HuggingFaceEmbeddings(
    # model_name="sentence-transformers/all-MiniLM-L6-v2"
    model_name="bkai-foundation-models/vietnamese-bi-encoder"
)

# ===== DB =====
db = Chroma(
    persist_directory=DB_PATH,
    embedding_function=embeddings
)

retriever = db.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 5
    }
)


llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)


def ask_question(question):
    try:
        docs = retriever.invoke(question)

        # ===== FILTER THEO KEYWORD =====
        filtered_docs = []
        q_lower = question.lower()

        for d in docs:
            if any(word in d.page_content.lower() for word in q_lower.split()):
                filtered_docs.append(d)

        if filtered_docs:
            docs = filtered_docs

        print("\n=== RETRIEVED DOCS ===")
        for d in docs:
            print(d.metadata.get("source"), "| page", d.metadata.get("page"))

        if not docs:
            return {
                "answer": "Tôi không tìm thấy thông tin.",
                "sources": []
            }

        docs = docs[:3]

        context = "\n\n".join([
            f"""
        Nguồn: {d.metadata.get('source')}
        Trang: {d.metadata.get('page')}

        {d.page_content[:1200]}
        """
            for d in docs
        ])
        print("\n=== CONTEXT ===")
        print(context[:2000])

        prompt = f"""
Bạn là trợ lý sinh viên.

Nhiệm vụ:
- Trả lời dựa trên CONTEXT.
- Nếu có thông tin liên quan → PHẢI trả lời.
- KHÔNG được trả lời "không tìm thấy" nếu có dữ liệu.

Quy tắc:
- Chỉ dùng thông tin trong CONTEXT
- Trả lời ngắn gọn, rõ ràng
- Không suy diễn

Nếu hoàn toàn không liên quan → trả lời:
"Không tìm thấy thông tin trong tài liệu"

CONTEXT:
{context}

CÂU HỎI:
{question}

TRẢ LỜI NGẮN GỌN:
"""
        print("\n=== CONTEXT ===")
        for doc in docs:
            print(doc.page_content[:200])

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
            "answer": "Hệ thống đang quá tải hoặc hết token. Đợi 1 lúc rồi thử lại.",
            "sources": []
        }


def reload_db():
    global db, retriever

    db = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embeddings
    )

    retriever = db.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 5
        }
    )