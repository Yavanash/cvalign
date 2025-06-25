import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


index_dir = "../vector-store/faiss_index"
embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device":"cpu"})

# Comprehensive file check
print("=== File System Debug ===")
print("Current working directory:", os.getcwd())
print("Target directory (relative):", index_dir)
print("Target directory (absolute):", os.path.abspath(index_dir))

for filename in ["index.faiss", "index.pkl"]:
    filepath = os.path.join(index_dir, filename)
    abs_filepath = os.path.abspath(filepath)
    
    print(f"\n{filename}:")
    print(f"  Relative path: {filepath}")
    print(f"  Absolute path: {abs_filepath}")
    print(f"  Exists: {os.path.exists(filepath)}")
    print(f"  Size: {os.path.getsize(filepath) if os.path.exists(filepath) else 'N/A'} bytes")
    print(f"  Readable: {os.access(filepath, os.R_OK) if os.path.exists(filepath) else 'N/A'}")
    print(f"  Permissions: {oct(os.stat(filepath).st_mode)[-3:] if os.path.exists(filepath) else 'N/A'}")

# Try loading with more detailed error handling
print("\n=== Loading Attempt ===")
try:
    vectore_store = FAISS.load_local(index_dir, embedder, allow_dangerous_deserialization=True)
    print("✓ Successfully loaded FAISS vector store!")
except Exception as e:
    print(f"✗ Error type: {type(e).__name__}")
    print(f"✗ Error message: {str(e)}")
    
    # Try to get more details from the traceback
    import traceback
    print("✗ Full traceback:")
    traceback.print_exc()