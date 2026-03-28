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

# retriever = db.as_retriever(
#     search_type="similarity",
#     search_kwargs={
#         "k": 5
#     }
# )

retriever = db.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 6,
        "fetch_k": 10,
        "lambda_mult": 0.7
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

        {d.page_content[:2000]}
        """
            for d in docs
        ])

        if len(context.strip()) < 5:
            return {
                "answer": "Không tìm thấy thông tin trong tài liệu",
                "sources": []
            }
        
        
        print("\n=== CONTEXT ===")
        print(context[:2000])

        prompt = f"""
Bạn là trợ lý sinh viên.

QUY TẮC BẮT BUỘC:
1. CHỈ được dùng thông tin trong CONTEXT
2. KHÔNG được suy diễn, KHÔNG được tự bổ sung
3. Nếu CONTEXT không chứa thông tin trả lời → trả lời chính xác:
   "Không tìm thấy thông tin trong tài liệu"
4. KHÔNG được trả lời dựa trên kiến thức bên ngoài

YÊU CẦU:
- Trả lời ngắn gọn, rõ ràng
- Nếu có nhiều ý → dùng bullet
- Nếu có số → giữ nguyên

CONTEXT:
{context}

CÂU HỎI:
{question}

TRẢ LỜI:
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
            "answer": "Hệ thống đang quá tải hoặc hết token. Đợi 1 lúc rồi thử lại.",
            "sources": []
        }


def reload_db():
    global db, retriever

    db = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embeddings
    )

    # retriever = db.as_retriever(
    #     search_type="similarity",
    #     search_kwargs={
    #         "k": 5
    #     }
    # )
    retriever = db.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 4,
            "fetch_k": 10,
            "lambda_mult": 0.7
        }
    )

