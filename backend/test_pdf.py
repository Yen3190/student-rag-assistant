from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("data/TV-THU MUC SACH-T12.2025.pdf")

pages = loader.load()

for p in pages:
    print("PAGE CONTENT:")
    print(p.page_content)