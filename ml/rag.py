from langchain.vectorstores import FAISS
from langchain.embeddings.ollama import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain

#vector database = FAISS
embedder = OllamaEmbeddings(model="nomic-embed-text")
vectore_store = FAISS.load_local("faiss_index", embeddings=embedder, allow_dangerous_deserialization=True)

# query = "what are the required skills for a data scientist"
# response = vectore_store.similarity_search(query=query, k=4)

#model = gemma:2b
model = Ollama(model="gemma:2b")

#prompt
prompt = ChatPromptTemplate.from_template("""
    Answer the following question based on only the provided context.
    Think step-by-step before providing a detailed answer.
    <context>
    {context}
    </context>
    Question: {input}
""")

#document chain
document_chain = create_stuff_documents_chain(model, prompt)

#retriever
retriever = vectore_store.as_retriever()

#retrieval chain
retrieval_chain = create_retrieval_chain(retriever, document_chain)

response = retrieval_chain.invoke({"input":"What are the skills required for a data scientist"})
print(response["answer"])