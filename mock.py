from fastapi import FastAPI
from ml_logic.document_loader.loader import extract_text
from ml_logic.data.preprocess import clean_text
import uvicorn
from typing import List
from pydantic import BaseModel, Field
from ml_logic.rag.main import eval_chain_mistral

class ScoreRequest(BaseModel):
    filename: str
    job_desc: str

class ScoreResponse(BaseModel):
    relevance_score: float = Field(default=0, description="Overall relevance score from 0-100")
    assessment: str = Field(default="",description="Overall assesment of the uploaded cv")
    strengths: List[str] = Field(default=[""], description="List of candidate's strengths")
    drawbacks: List[str] = Field(default=[""], description="Areas where candidate can improve")
    recommendations: List[str] = Field(default=[""], description="Actionable recommendations")

app = FastAPI()

@app.post("/score", response_model=ScoreResponse)
async def score(request_data: ScoreRequest):
    # You can do ML model scoring or other logic here
    print("Received:", request_data)
    #load data
    cv_file_path = "/app/uploads/" + request_data.filename
    docs = extract_text(cv_file_path) #this is a list of documents
    raw = ""
    for doc in docs:
        raw = raw + doc.page_content
    cv = clean_text(raw)

    #let jd is the job description entered by user
    jd=request_data.job_desc
    input_json = {"target_job_desc": jd, "cv":cv}

    result = await eval_chain_mistral.ainvoke(input_json)
    return result

if __name__=="__main__":
   uvicorn.run(app, host="localhost", port=8000)