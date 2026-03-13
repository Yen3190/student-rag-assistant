# from langchain_chroma import Chroma
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_groq import ChatGroq
# from dotenv import load_dotenv
# import os
# from chat_history import add_history


# load_dotenv()

# DB_PATH = "chroma_db"

# # Embedding model
# embeddings = HuggingFaceEmbeddings(
#     model_name="sentence-transformers/all-MiniLM-L6-v2"
# )

# # Load ChromaDB
# db = Chroma(
#     persist_directory=DB_PATH,
#     embedding_function=embeddings
# )

# # Retriever (MMR giúp lấy context đa dạng hơn)
# retriever = db.as_retriever(
#     search_type="mmr",
#     search_kwargs={
#         "k": 15,
#         "fetch_k": 50
#     }
# )

# # LLm Groq
# llm = ChatGroq(
#     model="llama-3.3-70b-versatile",
#     temperature=0,
#     api_key=os.getenv("GROQ_API_KEY")
# )

# def ask_question(query):

#     # Retrieve documents
#     docs = retriever.invoke(query)

#     # Nếu không tìm thấy tài liệu
#     if not docs:
#         return {
#             "answer": "Xin lỗi, tôi không tìm thấy thông tin liên quan trong tài liệu của trường.",
#             "sources": []
#         }

#     # Debug: xem retriever lấy đoạn nào
#     print("\nRetrieved documents:\n")

#     for d in docs:
#         print(d.metadata)
#         print(d.page_content[:200])
#         print("------")

#     # Build context cho LLM
#     context = "\n\n".join(
#         [
#             f"""
# Nguồn: {d.metadata.get('source')}
# Trang: {d.metadata.get('page')}

# {d.page_content}
# """
#             for d in docs
#         ]
#     )

#     # Prompt cho LLM
#     prompt = f"""
# Bạn là trợ lý học vụ của trường đại học.

# Chỉ được trả lời dựa trên thông tin trong tài liệu dưới đây.
# Không được tự suy đoán hoặc thêm thông tin ngoài tài liệu.

# Nếu tài liệu không chứa câu trả lời, hãy nói:
# "Tôi không tìm thấy thông tin trong tài liệu."

# Tài liệu:

# {context}

# Câu hỏi:
# {query}

# Hãy trả lời rõ ràng, đầy đủ và nếu có thể hãy nêu nguồn và trang.
# """

#     # Gọi LLM
#     response = llm.invoke(prompt)

#     # Lấy danh sách nguồn (không trùng)
#     sources = list({
#         f"{d.metadata.get('source')} (page {d.metadata.get('page')})"
#         for d in docs
#     })

#     return {
#         "answer": response.content,
#         "sources": sources
#     }


from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from chat_history import add_history

load_dotenv()

DB_PATH = "chroma_db"

# Embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load ChromaDB
db = Chroma(
    persist_directory=DB_PATH,
    embedding_function=embeddings
)

# Retriever
retriever = db.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 6,
        "fetch_k": 20
    }
)

# LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)


def ask_question(query):

    docs = retriever.invoke(query)

    docs = docs[:6]

    if not docs:
        return {
            "answer": "Xin lỗi, tôi không tìm thấy thông tin liên quan trong tài liệu của trường.",
            "sources": []
        }

    print("\nRetrieved documents:\n")

    for d in docs:
        print(d.metadata)
        print(d.page_content[:200])
        print("------")

    context = "\n\n".join(
        [
            f"""
Nguồn: {d.metadata.get('source')}
Trang: {d.metadata.get('page')}

{d.page_content[:1200]}
"""
            for d in docs
        ]
    )

    prompt = f"""
Bạn là trợ lý học vụ của trường đại học.

Nhiệm vụ của bạn là trả lời câu hỏi của sinh viên dựa hoàn toàn trên tài liệu nội bộ của trường.

QUY TẮC:
1. Chỉ sử dụng thông tin trong tài liệu.
2. Không được suy đoán hoặc thêm thông tin ngoài tài liệu.
3. Nếu tài liệu không chứa câu trả lời, hãy nói:
"Tôi không tìm thấy thông tin trong tài liệu."
4. Khi trả lời, nếu có thể hãy trích dẫn nguồn và trang.

---------------------
TÀI LIỆU THAM KHẢO
---------------------

{context}

---------------------
CÂU HỎI
---------------------

{query}

---------------------
CÂU TRẢ LỜI
---------------------
"""

    try:
        response = llm.invoke(prompt)
    except Exception as e:
        return {
            "answer": "Lỗi khi gọi AI model.",
            "sources": []
        }

    add_history(query, response.content)

    sources = list({
        f"{d.metadata.get('source')} (page {d.metadata.get('page')})"
        for d in docs
    })

    return {
        "answer": response.content,
        "sources": sources
    }