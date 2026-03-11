from fastapi import FastAPI, UploadFile
import shutil

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Student RAG Assistant API"}

@app.post("/upload")
async def upload_file(file: UploadFile):

    path = f"data/pdf/{file.filename}"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file.filename}

@app.post("/chat")
def chat(question: str):

    answer = rag_chain.invoke({"query": question})

    return {
        "answer": answer["result"],
        "sources": [
            doc.metadata["source"]
            for doc in answer["source_documents"]
        ]
    }