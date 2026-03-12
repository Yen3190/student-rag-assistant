from fastapi import FastAPI
from pydantic import BaseModel
from rag_engine import ask_question

app = FastAPI()

class Question(BaseModel):
    question: str

@app.get("/")
def home():
    return {"message": "Student RAG Assistant Running"}

@app.post("/chat")
def chat(q: Question):

    result = ask_question(q.question)

    return result