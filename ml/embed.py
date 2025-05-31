import pandas as pd
from preprocess import clean_text
from langchain_community.embeddings import OllamaEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
df = pd.read_csv("hf://datasets/brackozi/Resume/UpdatedResumeDataSet.csv")
# print(df.head(3))

df["processed_txt"] = df["Resume"].apply(clean_text)
embedder = OllamaEmbeddings(model="nomic-embed-text")
chunker = SemanticChunker(embedder)

docs = []

for _,row in df.iterrows():
    chunks = chunker.split_text(row["processed_txt"])

    for i,chunk in enumerate(chunks):
        docs.append(Document(
            page_content=chunk,
            metadata={
                "chunk_no": i,
                "category": row["Category"]
            }
        ))

db = FAISS.from_documents(docs, embedder)
db.save_local("faiss_index")