import os
import shutil
import pytesseract
import re 
from PIL import Image
from pdf2image import convert_from_path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

import platform

#pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


DATA_PATH = "data"
DB_PATH = "chroma_db"

def normalize_text(text):
    import re

    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)

    # gộp chữ rời
    text = re.sub(r"(\b\w\b\s+){2,}\b\w\b", lambda m: m.group(0).replace(" ", ""), text)

    fixes = {
        "TrtrdNG": "Trường",
        "Gidm": "Giám",
        "DUG": "DỤC",
        "Cdc": "Các",
        "Lim": "Lưu",
    }

    for k, v in fixes.items():
        text = text.replace(k, v)

    return text.strip()

# ================= OCR =================
def extract_text_from_scan(pdf_path, filename):
    print("Running OCR for:", filename)

    # images = convert_from_path(
    #     pdf_path,
    #     poppler_path=r"C:\poppler-25.12.0\Library\bin"
    # )
    if platform.system() == "Windows":
        images = convert_from_path(
            pdf_path,
            poppler_path=r"C:\poppler-25.12.0\Library\bin"
        )
    else:
        images = convert_from_path(pdf_path)

    docs = []

    for i, img in enumerate(images):

        img = img.convert("L")  
        img = img.point(lambda x: 0 if x < 150 else 255)
        img = img.resize((img.width * 2, img.height * 2))

        text = pytesseract.image_to_string(
            img,
            lang="vie+eng",
            config="--oem 3 --psm 4"
        )

        text = normalize_text(text)

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



def is_broken_text(text):
    words = text.split()
    if len(words) == 0:
        return True

    avg_len = sum(len(w) for w in words) / len(words)

    if avg_len < 4:
        return True

    if text.count("\n") > 20:
        return True

    return False


# ================= INGEST =================
def ingest():

    docs = []

    existing_sources = set()

    embeddings = HuggingFaceEmbeddings(
        model_name="bkai-foundation-models/vietnamese-bi-encoder"
        #model_name="sentence-transformers/all-MiniLM-L6-v2"
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

        if file in existing_sources:
            print("Skipping (already in DB):", file)
            continue

        path = os.path.join(DATA_PATH, file)

        print("\nProcessing:", file)

        loader = PyPDFLoader(path)
        pages = loader.load()

        print("Sample content:", pages[0].page_content[:200])

        text_length = sum(len(p.page_content.strip()) for p in pages)


        raw_text = " ".join(p.page_content for p in pages)

        if text_length < 1000 or is_broken_text(raw_text):
            print("Using OCR")
            docs.extend(extract_text_from_scan(path, file))
        else:
            print("Using normal PDF loader")
            docs.extend(pages)

    print("\nTotal pages:", len(docs))

    if not docs:
        print("No new documents to ingest")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
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