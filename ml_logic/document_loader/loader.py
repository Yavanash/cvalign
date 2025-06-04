from langchain_community.document_loaders import PyMuPDFLoader, Docx2txtLoader
from pathlib import Path

# print(file_type)
def extract_text(file_path):
    f = Path(file_path)
    file_type = f.suffix
    if file_type == ".pdf":
        loader = PyMuPDFLoader(file_path)

    if file_type == ".docx":
        loader = Docx2txtLoader(file_path)

    docs = loader.load()
    # print(type(docs[0].page_content))
    return docs