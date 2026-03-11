from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

def get_vector_db(chunks):

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectordb = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory="./vectorstore"
    )

    vectordb.persist()

    return vectordb