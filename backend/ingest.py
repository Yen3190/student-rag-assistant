# import os
# import shutil
# import pytesseract

# from PIL import Image
# from pdf2image import convert_from_path

# from langchain_community.document_loaders import PyPDFLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_core.documents import Document
# from langchain_chroma import Chroma
# from langchain_huggingface import HuggingFaceEmbeddings


# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# DATA_PATH = "data"
# DB_PATH = "chroma_db"


# def extract_text_from_scan(pdf_path, filename):

#     print("Running OCR for:", filename)

#     images = convert_from_path(
#         pdf_path,
#         poppler_path=r"C:\poppler-25.12.0\Library\bin"
#     )

#     docs = []

#     for i, img in enumerate(images):

#         text = pytesseract.image_to_string(img, lang="vie+eng")

#         if not text.strip():
#             text = "[OCR failed]"

#         docs.append(
#             Document(
#                 page_content=text,
#                 metadata={
#                     "source": filename,
#                     "page": i + 1
#                 }
#             )
#         )

#     return docs


# def ingest():

#     # Xóa database cũ
#     if os.path.exists(DB_PATH):
#         shutil.rmtree(DB_PATH)

#     docs = []

#     for file in os.listdir(DATA_PATH):

#         if not file.endswith(".pdf"):
#             continue

#         path = os.path.join(DATA_PATH, file)

#         print("\nProcessing:", file)

#         loader = PyPDFLoader(path)

#         pages = loader.load()

#         # kiểm tra PDF có text không
#         text_length = sum(len(p.page_content.strip()) for p in pages)

#         if text_length < 50:
#             print("PDF scan detected -> using OCR")

#             ocr_docs = extract_text_from_scan(path, file)

#             docs.extend(ocr_docs)

#         else:
#             print("PDF text detected")

#             for p in pages:
#                 p.metadata["source"] = file

#             docs.extend(pages)

#     print("\nTotal pages:", len(docs))

#     # chia chunk
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000,
#         chunk_overlap=200
#     )

#     chunks = splitter.split_documents(docs)

#     print("Total chunks:", len(chunks))

#     # embedding
#     embeddings = HuggingFaceEmbeddings(
#         model_name="sentence-transformers/all-MiniLM-L6-v2"
#     )

#     # lưu chroma
#     Chroma.from_documents(
#         chunks,
#         embeddings,
#         persist_directory=DB_PATH
#     )

#     print("\nIngest completed")


# if __name__ == "__main__":
#     ingest()

import os
import pytesseract

from pdf2image import convert_from_path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


# đường dẫn OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

POPPLER_PATH = r"C:\poppler-25.12.0\Library\bin"

DATA_PATH = "data"
DB_PATH = "chroma_db"


def extract_text_from_scan(pdf_path, filename):
    """
    OCR cho PDF scan
    """

    print("Running OCR for:", filename)

    images = convert_from_path(
        pdf_path,
        poppler_path=POPPLER_PATH
    )

    docs = []

    for i, img in enumerate(images):

        text = pytesseract.image_to_string(img, lang="vie+eng")

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

    print("Starting ingest process...\n")

    # embedding model
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # mở ChromaDB nếu đã tồn tại
    db = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embeddings
    )

    # lấy danh sách file đã ingest
    existing_sources = set()

    try:
        data = db.get()

        if data and "metadatas" in data:

            for m in data["metadatas"]:
                if m and "source" in m:
                    existing_sources.add(m["source"])

    except Exception as e:
        print("No existing database yet")

    docs = []

    for file in os.listdir(DATA_PATH):

        if not file.endswith(".pdf"):
            continue

        if file in existing_sources:
            print("Skipping already ingested file:", file)
            continue

        path = os.path.join(DATA_PATH, file)

        print("\nProcessing:", file)

        loader = PyPDFLoader(path)

        pages = loader.load()

        # kiểm tra PDF có text không
        text_length = sum(len(p.page_content.strip()) for p in pages)

        if text_length < 50:

            print("PDF scan detected → using OCR")

            ocr_docs = extract_text_from_scan(path, file)

            docs.extend(ocr_docs)

        else:

            print("PDF text detected")

            for p in pages:
                p.metadata["source"] = file

            docs.extend(pages)

    if len(docs) == 0:
        print("\nNo new documents to ingest")
        return

    print("\nTotal pages:", len(docs))

    # chia chunk
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(docs)

    print("Total chunks:", len(chunks))

    # add vào ChromaDB
    db.add_documents(chunks)

    print("\nDocuments added to ChromaDB successfully!")


if __name__ == "__main__":
    ingest()