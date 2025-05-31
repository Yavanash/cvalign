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

def extract_jd_text(jd):
    #jd is the job description
    req_skills = jd["req_skills"]
    exp = jd["exp"]
    traits = jd["traits"]
    s = f"Required skills are ${req_skills}. Required experience is ${exp}. Required traits are ${traits}."
    return s