from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
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

# retriever = db.as_retriever(
#     search_type="mmr",
#     search_kwargs={
#         "k":6,
#         "fetch_k":20
#     }
# )

retriever = db.as_retriever(
    search_kwargs={"k":8}
)

llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

def ask_question(query):

    docs = retriever.invoke(query)

    context = "\n\n".join(
        [f"{d.page_content}\n(Source:{d.metadata})" for d in docs]
    )

    prompt = f"""
Bạn là trợ lý học vụ của trường đại học.

Dựa vào các thông tin sau từ tài liệu của trường để trả lời.

{context}

Câu hỏi: {query}

Trả lời rõ ràng và nếu có thể hãy nhắc đến nguồn.
"""

    response = llm.invoke(prompt)

    sources = []

    for d in docs:
        sources.append(
            f"{d.metadata.get('source')} (page {d.metadata.get('page')})"
        )

    return {
        "answer": response.content,
        "sources": list(set(sources))
    }