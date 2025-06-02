from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
import time

class ScoreRequest(BaseModel):
    filename: str

class ScoreResponse(BaseModel):
    status: str
    score: float
    remarks: str

app = FastAPI()

@app.post("/score", response_model=ScoreResponse)
def score(request_data: ScoreRequest):
    # You can do ML model scoring or other logic here
    print("Received:", request_data)
    time.sleep(10)
    # Example response
    return ScoreResponse(
        status="success",
        score=0.87,
        remarks="Processed successfully"
    )
if __name__=="__main__":
   uvicorn.run(app, host="localhost", port=8000)