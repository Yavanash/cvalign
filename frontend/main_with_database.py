# Alternative main.py with database integration
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional, List
import tempfile
import os
from datetime import datetime
from pydantic import BaseModel

from database import get_db, add_to_leaderboard_db, get_leaderboard_db, LeaderboardDB

app = FastAPI(title="Resume Screener API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class LeaderboardEntry(BaseModel):
    username: str
    score: float
    timestamp: Optional[str] = None
    job_title: Optional[str] = None

class LeaderboardResponse(BaseModel):
    data: List[LeaderboardEntry]
    total: int

@app.post("/score")
async def score_resume(
    pdf: UploadFile = File(...),
    job_desc: str = Form(...),
    candidate_name: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Score resume and automatically add to database leaderboard"""
    
    if not job_desc.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty")
    
    try:
        pdf_content = await pdf.read()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(pdf_content)
            temp_file_path = temp_file.name
        
        # Your LLM processing
        result = analyze_resume_with_llm(temp_file_path, job_desc, candidate_name)
        
        os.unlink(temp_file_path)
        
        # Add to database leaderboard
        add_to_leaderboard_db(
            db, 
            username=candidate_name or "Anonymous",
            score=result["score"],
            job_title=extract_job_title(job_desc)
        )
        
        return {
            "relevance_score": result["score"],
            "candidate_name": candidate_name or "Anonymous",
            "analysis": result.get("analysis", ""),
            "status": "success"
        }
        
    except Exception as e:
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/v1/leaderboard")
async def get_leaderboard(db: Session = Depends(get_db)):
    """Get leaderboard from database"""
    try:
        entries = get_leaderboard_db(db)
        
        data = [
            {
                "username": entry.username,
                "score": entry.score,
                "job_title": entry.job_title,
                "timestamp": entry.timestamp.isoformat() if entry.timestamp else None
            }
            for entry in entries
        ]
        
        return {"data": data, "total": len(data)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch leaderboard: {str(e)}")

# Include your other functions here...
def analyze_resume_with_llm(pdf_path: str, job_description: str, candidate_name: str = None):
    # Your LLM processing logic
    return {
        "score": 85.5,
        "analysis": "Good match for the position",
        "skills": ["Python", "ML"]
    }

def extract_job_title(job_description: str) -> str:
    return "Software Engineer"  # Implement your logic

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
