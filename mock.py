from fastapi import FastAPI
import uvicorn
from typing import List
from pydantic import BaseModel, Field
import time
import requests

class ScoreRequest(BaseModel):
    filename: str
    job_desc: str

class ScoreResponse(BaseModel):
    relevance_score: float = Field(default=0, description="Overall relevance score from 0-100")
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
    #load data
    # docs = extract_text(request_data) #this is a list of documents
    # raw = ""
    # for doc in docs:
    #     raw = raw + doc.page_content
    # cv = clean_text(raw)

    #let jd is the job description entered by user
    jd=request_data.job_description
    input_json = {"target_job_desc": jd, "cv":cv}

    output = mistral_response(input_json)
    return output

if __name__=="__main__":
   uvicorn.run(app, host="localhost", port=9000)