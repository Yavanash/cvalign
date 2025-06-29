from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import tempfile
import os
import json
from datetime import datetime
from pydantic import BaseModel, Field
from ml_logic.document_loader.loader import extract_text
from ml_logic.data.preprocess import clean_text
from ml_logic.rag.main import eval_chain_mistral

app = FastAPI(title="Resume Screener API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
uploads_dir = "backend/uploads"
os.makedirs(uploads_dir, exist_ok=True)

# In-memory storage for leaderboard (replace with database in production)
leaderboard_data = []

# Pydantic models
class LeaderboardEntry(BaseModel):
    username: str
    score: float
    timestamp: Optional[str] = None
    job_title: Optional[str] = None

class LeaderboardResponse(BaseModel):
    data: List[LeaderboardEntry]
    total: int

class ScoreResponse(BaseModel):
    relevance_score: float = Field(default=0, description="Overall relevance score from 0-100")
    assessment: str = Field(default="", description="Overall assessment of the uploaded cv")
    strengths: List[str] = Field(default=[], description="List of candidate's strengths")
    drawbacks: List[str] = Field(default=[], description="Areas where candidate can improve")
    recommendations: List[str] = Field(default=[], description="Actionable recommendations")

# Your existing score endpoint
@app.post("/score", response_model=ScoreResponse)
async def score_resume(
    pdf: UploadFile = File(...),
    job_desc: str = Form(...),
    candidate_name: Optional[str] = Form(None)
):
    """
    Analyze resume against job description using LLM
    """
    # Validate inputs
    if not job_desc.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty")
    
    if pdf.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        # Read PDF content
        pdf_content = await pdf.read()
        
        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(pdf_content)
            temp_file_path = temp_file.name
        
        # Process with your LLM
        result = analyze_resume_with_llm(temp_file_path, job_desc, candidate_name)
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        # Automatically add to leaderboard
        leaderboard_entry = LeaderboardEntry(
            username=candidate_name or "Anonymous",
            score=result["score"],
            timestamp=datetime.now().isoformat(),
            job_title=extract_job_title(job_desc)  # Optional: extract job title
        )
        leaderboard_data.append(leaderboard_entry.dict())
        
        return ScoreResponse(
            relevance_score=result["score"],
            candidate_name=candidate_name or "Anonymous",
            analysis=result.get("analysis", ""),
            skills_matched=result.get("skills", []),
            status="success"
        )
        
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

# Upload endpoint (if you want to separate upload from scoring)
@app.post("/v1/upload", response_model=ScoreResponse)
async def upload_file(
    pdf: UploadFile = File(...),
    job_desc: str = Form(...),
    candidate_name: Optional[str] = Form(None)
):
    """
    Upload and process resume - calls score endpoint internally
    """
    try:
        # You can either:
        # Option 1: Just call the score endpoint internally
        result = await score_resume(pdf, job_desc, candidate_name)
        return result
        
        # Option 2: Or implement separate upload logic
        # pdf_content = await pdf.read()
        # file_id = save_file_temporarily(pdf_content, pdf.filename)
        # return {"file_id": file_id, "message": "File uploaded successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# Get leaderboard
@app.get("/v1/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard():
    """
    Get current leaderboard sorted by score
    """
    try:
        # Sort by score descending
        sorted_data = sorted(leaderboard_data, key=lambda x: x["score"], reverse=True)
        
        return LeaderboardResponse(
            data=sorted_data,
            total=len(sorted_data)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch leaderboard: {str(e)}")

# Add entry to leaderboard (optional - for manual additions)
@app.post("/v1/leaderboard")
async def add_to_leaderboard(entry: LeaderboardEntry):
    """
    Manually add entry to leaderboard
    """
    try:
        entry_dict = entry.dict()
        if not entry_dict.get("timestamp"):
            entry_dict["timestamp"] = datetime.now().isoformat()
        
        leaderboard_data.append(entry_dict)
        
        return {"message": "Entry added to leaderboard", "entry": entry_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add to leaderboard: {str(e)}")

# Clear leaderboard (useful for testing)
@app.delete("/v1/leaderboard")
async def clear_leaderboard():
    """
    Clear all leaderboard entries
    """
    global leaderboard_data
    leaderboard_data = []
    return {"message": "Leaderboard cleared", "total_cleared": len(leaderboard_data)}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "leaderboard_entries": len(leaderboard_data),
        "uploads_dir": uploads_dir,
        "uploads_dir_exists": os.path.exists(uploads_dir)
    }

# Leaderboard statistics endpoint
@app.get("/leaderboard/stats")
async def leaderboard_stats():
    """
    Get leaderboard statistics
    """
    if not leaderboard_data:
        return {
            "total_entries": 0,
            "average_score": 0,
            "highest_score": 0,
            "lowest_score": 0
        }
    
    scores = [entry["score"] for entry in leaderboard_data]
    
    return {
        "total_entries": len(leaderboard_data),
        "average_score": sum(scores) / len(scores),
        "highest_score": max(scores),
        "lowest_score": min(scores),
        "latest_entry": max(leaderboard_data, key=lambda x: x.get("timestamp", ""))
    }

# Your LLM processing function
def analyze_resume_with_llm(pdf_path: str, job_description: str, candidate_name: str = None):
    """
    Replace this with your actual LLM processing logic
    """
    print(f"Analyzing resume for: {candidate_name}")
    print(f"Job Description: {job_description[:100]}...")
    print(f"PDF Path: {pdf_path}")
    
    # TODO: Replace with your actual LLM call
    # Example: score = your_llm_model.analyze(pdf_path, job_description)
    
    # Mock response - replace with your LLM output
    return {
        "score": 85.5,  # Your LLM's relevance score (0-100)
        "analysis": "Good match for the position based on skills and experience",
        "skills": ["Python", "Machine Learning", "Data Analysis"]
    }

def extract_job_title(job_description: str) -> str:
    """
    Extract job title from job description (optional)
    """
    lines = job_description.split('\n')
    
    # Look for common job title indicators
    for line in lines[:5]:  # Check first 5 lines
        line = line.strip()
        if any(keyword in line.lower() for keyword in [
            'position:', 'role:', 'job title:', 'title:', 'hiring for', 'looking for'
        ]):
            # Extract the part after the colon or keyword
            if ':' in line:
                return line.split(':', 1)[1].strip()
            else:
                return line.strip()
    
    # Fallback: look for common job titles in the text
    common_titles = [
        'software engineer', 'data scientist', 'product manager', 'designer',
        'developer', 'analyst', 'manager', 'director', 'specialist', 'consultant'
    ]
    
    job_desc_lower = job_description.lower()
    for title in common_titles:
        if title in job_desc_lower:
            return title.title()
    
    return "Software Engineer"  # Default fallback

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080)  # Changed to 8080 to match frontend
