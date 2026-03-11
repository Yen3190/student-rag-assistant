from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI

def create_rag_chain(vectordb):

    retriever = vectordb.as_retriever()

    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        temperature=0.2
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    return qa_chain