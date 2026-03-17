import os
import shutil
import pytesseract

from PIL import Image
from pdf2image import convert_from_path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

DATA_PATH = "data"
DB_PATH = "chroma_db"


def extract_text_from_scan(pdf_path, filename):

    print("Running OCR for:", filename)

    images = convert_from_path(
        pdf_path,
        poppler_path=r"C:\poppler-25.12.0\Library\bin"
    )

    docs = []

    for i, img in enumerate(images):

        text = pytesseract.image_to_string(
            img,
            lang="vie+eng",
            config="--oem 3 --psm 6"   # 🔥 FIX TABLE
        )

        if not text.strip():
            text = "[OCR failed]"

        docs.append(
            Document(
                page_content=text,
                metadata={
                    "source": filename,
                    "page": i + 1
                }
            )
        )

    return docs


def ingest():

    docs = []

    # ===== LOAD EXISTING FILES IN DB =====
    existing_sources = set()

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    if os.path.exists(DB_PATH):
        try:
            db = Chroma(
                persist_directory=DB_PATH,
                embedding_function=embeddings
            )

            data = db.get()

            if data and data.get("metadatas"):
                existing_sources = set(
                    m["source"] for m in data["metadatas"]
                )

            print("Existing files in DB:", existing_sources)

        except Exception as e:
            print("Cannot load existing DB:", e)

    for file in os.listdir(DATA_PATH):

        if not file.endswith(".pdf"):
            continue

        # # ===== SKIP FILE ĐÃ CÓ =====
        # if file in existing_sources:
        #     print("Skipping (already in DB):", file)
        #     continue

        path = os.path.join(DATA_PATH, file)

        print("\nProcessing:", file)

        loader = PyPDFLoader(path)
        pages = loader.load()

        print("Sample content:", pages[0].page_content[:200])

        text_length = sum(len(p.page_content.strip()) for p in pages)

        if text_length < 200:
            print("PDF scan detected -> using OCR")
            docs.extend(extract_text_from_scan(path, file))
        else:
            print("PDF text detected")
            for p in pages:
                p.metadata["source"] = file
            docs.extend(pages)

    print("\nTotal pages:", len(docs))

    # ===== KHÔNG CÓ FILE MỚI =====
    if not docs:
        print("No new documents to ingest")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(docs)

    print("Total chunks:", len(chunks))

    db = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embeddings
    )

    db.add_documents(chunks)
    

    print("\nIngest completed")


if __name__ == "__main__":
    ingest()