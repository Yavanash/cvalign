import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings #embedder
from langchain.text_splitter import RecursiveCharacterTextSplitter #chunking
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DataFrameLoader

df = pd.read_csv("../data/data.csv")
# print(df.head(3))
loader = DataFrameLoader(df, page_content_column="pjdesc")
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=500)
embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": "cpu"})

doc_chunks = text_splitter.split_documents(documents)
# print(len(doc_chunks))
db = FAISS.from_documents(doc_chunks, embedder)
db.save_local("faiss_index")