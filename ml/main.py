from loader import  extract_text, extract_jd_text
from preprocess import clean_text
import os
from dotenv import load_dotenv

load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

file_path = "SravaniCV.pdf"

def main(file_path):
    loaded = extract_text(file_path)
    for page in loaded:
        docs = page.page_content
        #preprocessing
        docs = clean_text(docs)
        #chunking

        print(docs)

jd_text = "" #jd is the job description
if __name__ == "__main__":
    main(file_path)