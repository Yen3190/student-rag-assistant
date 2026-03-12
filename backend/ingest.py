import os
import shutil
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

DATA_PATH = "data"
DB_PATH = "chroma_db"


def ingest():

    # Xóa database cũ
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)

    docs = []

    # Đọc tất cả file PDF
    for file in os.listdir(DATA_PATH):

        print("Found file:", file)

        if file.endswith(".pdf"):

            path = os.path.join(DATA_PATH, file)

            print("Loading:", path)

            loader = PyPDFLoader(path)

            pages = loader.load()

            print("Pages:", len(pages))

            for p in pages:
                p.metadata["source"] = file

            docs.extend(pages)

    print("Total pages:", len(docs))

    # Chia nhỏ text
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=150
    )

    chunks = splitter.split_documents(docs)

    print("Total chunks:", len(chunks))

    print("Example chunk:\n")
    print(chunks[0].page_content)
    print("--------------")

    for c in chunks:
        if "Công nghệ" in c.page_content or "Artificial Intelligence" in c.page_content:
            print("FOUND IT CHUNK:")
            print(c.page_content)


    # Embedding model miễn phí
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Lưu vào ChromaDB
    Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory=DB_PATH
    )

    print("Ingest completed")


if __name__ == "__main__":
    ingest()