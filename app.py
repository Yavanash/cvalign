from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import tempfile
import os
from glob import glob
import uvicorn
import warnings
from datetime import datetime
from pydantic import BaseModel, Field
from ml_logic.document_loader.loader import extract_text
from ml_logic.data.preprocess import clean_text
from ml_logic.rag.main import eval_chain_mistral

warnings.filterwarnings("ignore", category=UserWarning)
app = FastAPI(title="Resume Screener API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("backend/uploads", exist_ok=True)
leaderboard_data = []

class LeaderboardEntry(BaseModel):
    username: str
    score: float

class LeaderboardResponse(BaseModel):
    data: List[LeaderboardEntry]
    total: int

class ScoreRequest(BaseModel):
    pdf: UploadFile = File(...)
    job_desc: str = Form(...)
    candidate_name: Optional[str] = Form(None)

class ScoreResponse(BaseModel):
    relevance_score: float = Field(default=0, description="Overall relevance score from 0-100")
    assessment: str = Field(default="", description="Overall assessment of the uploaded cv")
    strengths: List[str] = Field(default=[], description="List of candidate's strengths")
    drawbacks: List[str] = Field(default=[], description="Areas where candidate can improve")
    recommendations: List[str] = Field(default=[], description="Actionable recommendations")

async def process_resume_with_llm(filepath: str, job_description: str):
    docs = extract_text(filepath)
    txt = "".join(doc.page_content for doc in docs)
    cv = clean_text(txt)
    input_data = {"target_job_desc": job_description, "cv": cv}
    result = await eval_chain_mistral.ainvoke(input_data)
    return result

@app.post("/score", response_model=List[ScoreResponse])
async def score_resume(
    pdfs: List[UploadFile] = File(...),
    job_desc: str = Form(...),
    candidate_name: Optional[str] = Form(None)
):
    results = []
    for pdf in pdfs:
        try:
            pdf_content = await pdf.read()
    
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(pdf_content)
                temp_file_path = temp_file.name
            result = await process_resume_with_llm(temp_file_path, job_desc)
            results.append(result)
            os.unlink(temp_file_path)
            
            leaderboard_entry = LeaderboardEntry(
                username=candidate_name or "Anonymous",
                score=result.relevance_score,
                timestamp=datetime.now().isoformat(),
            )
            leaderboard_data.append(leaderboard_entry.dict())
        
        except Exception as e:
            if 'temp_file_path' in locals():
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
            raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    return results

@app.get("/v1/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard():
    sorted_data = sorted(leaderboard_data, key=lambda x: x["score"], reverse=True)
    return LeaderboardResponse(data=sorted_data, total=len(sorted_data))

@app.post("/v1/leaderboard")
async def add_to_leaderboard(entry: LeaderboardEntry):
    entry_dict = entry.dict()
    if not entry_dict.get("timestamp"):
        entry_dict["timestamp"] = datetime.now().isoformat()
    
    leaderboard_data.append(entry_dict)
    return {"message": "Entry added to leaderboard", "entry": entry_dict}

@app.delete("/v1/leaderboard")
async def clear_leaderboard():
    global leaderboard_data
    leaderboard_data = []
    return {"message": "Leaderboard cleared"}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080)