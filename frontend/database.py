# Optional: Database integration for persistent storage
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# SQLite database for simplicity (replace with PostgreSQL/MySQL in production)
SQLALCHEMY_DATABASE_URL = "sqlite:///./resume_screener.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class LeaderboardDB(Base):
    __tablename__ = "leaderboard"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    score = Column(Float)
    job_title = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Database functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def add_to_leaderboard_db(db, username: str, score: float, job_title: str = None):
    db_entry = LeaderboardDB(
        username=username,
        score=score,
        job_title=job_title
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

def get_leaderboard_db(db):
    return db.query(LeaderboardDB).order_by(LeaderboardDB.score.desc()).all()
