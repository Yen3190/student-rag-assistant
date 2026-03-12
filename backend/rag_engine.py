from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = "chroma_db"

# Embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load vector database
db = Chroma(
    persist_directory=DB_PATH,
    embedding_function=embeddings
)

# Retriever
retriever = db.as_retriever(search_kwargs={"k":3})

# LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0
)

def ask_question(query):

    docs = retriever.invoke(query)

    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""
Bạn là trợ lý học vụ của trường đại học.

Chỉ trả lời dựa trên thông tin sau:

{context}

Câu hỏi: {query}

Trả lời:
"""

    response = llm.invoke(prompt)

    sources = []

    for doc in docs:
        sources.append(doc.metadata.get("source","unknown"))

    return {
        "answer": response.content,
        "sources": list(set(sources))
    }