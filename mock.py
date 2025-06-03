from ml.document_loader.loader import  extract_text
from ml.data.preprocess import clean_text
from fastapi import FastAPI
import uvicorn
from typing import List
from pydantic import BaseModel, Field
import time
import requests

class ScoreRequest(BaseModel):
    filename: str

class ScoreResponse(BaseModel):
    relevance_score: int = Field(default=0, description="Overall relevance score from 0-100")
    assessment: str = Field(default="",description="Overall assesment of the uploaded cv")
    strengths: List[str] = Field(default=[""], description="List of candidate's strengths")
    drawbacks: List[str] = Field(default=[""], description="Areas where candidate can improve")
    recommendations: List[str] = Field(default=[""], description="Actionable recommendations")

#input json:{"target_job_desc": "", "cv":""}
def gemma_response(input_json):
    response = requests.post("http://localhost:8000/score/gemma/invoke", json={"input": input_json})
    return response.json()["output"]

def mistral_response(input_json):
    response = requests.post("http://localhost:8000/score/mistral/invoke", json={"input": input_json})
    return response.json()["output"]

app = FastAPI()

@app.post("/score", response_model=ScoreResponse)
def score(request_data: ScoreRequest):
    # You can do ML model scoring or other logic here
    print("Received:", request_data)
    time.sleep(10)
    
    #load data
    docs = extract_text(request_data) #this is a list of documents
    raw = ""
    for doc in docs:
        raw = raw + doc.page_content
    cv = clean_text(raw)

    #let jd is the job description entered by user
    jd=""
    input_json = {"target_job_desc": jd, "cv":cv}
    #if input is small call gemma function, else call mistral....(if error due to gemma call mistral)

if __name__=="__main__":
   uvicorn.run(app, host="localhost", port=8000)