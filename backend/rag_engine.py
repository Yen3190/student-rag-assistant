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

retriever = db.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k":6,
        "fetch_k":20
    }
)

llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

def ask_question(query):

    docs = retriever.invoke(query)

    for doc in docs:
        print(doc.metadata)

    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""
Bạn là trợ lý học vụ của trường đại học.

Hãy sử dụng thông tin từ các tài liệu sau để trả lời câu hỏi.

{context}

Câu hỏi: {query}

Trả lời:
"""

    response = llm.invoke(prompt)

    sources = list(set([doc.metadata.get("source","unknown") for doc in docs]))

    return {
        "answer": response.content,
        "sources": sources
    }