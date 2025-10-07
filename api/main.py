from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List
from .database import get_db, Hackathon, init_db

app = FastAPI(
    title="Palmer API",
    description="All hackathons in the palm of your hand",
    version="0.1.0",
)


# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/")
def root():
    """Root endpoint with API info"""
    return {
        "name": "Palmer API",
        "version": "0.1.0",
        "description": "Hackathon aggregation API",
        "endpoints": {
            "/hackathons": "Get all hackathons",
            "/hackathons/{id}": "Get specific hackathon",
            "/stats": "Get statistics",
            "/health": "Health check",
        },
    }


@app.get("/health")
def health_check():
    """Simple health check"""
    return {"status": "healthy", "service": "palmer-api"}


@app.get("/hackathons")
def get_all_hackathons(db: Session = Depends(get_db)):
    """
    Get all hackathons
    """
    hackathons = db.query(Hackathon).all()

    return {
        "count": len(hackathons),
        "hackathons": [hack.to_dict() for hack in hackathons],
    }


@app.get("/hackathons/{hackathon_id}")
def get_hackathon(hackathon_id: int, db: Session = Depends(get_db)):
    """
    Get a specific hackathon by ID
    """
    hackathon = db.query(Hackathon).filter(Hackathon.id == hackathon_id).first()

    if not hackathon:
        return {"error": "Hackathon not found"}

    return hackathon.to_dict()


@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """
    Get statistics about scraped data
    """
    total = db.query(Hackathon).count()

    # Count by status
    statuses = db.query(Hackathon.status).distinct().all()
    status_counts = {}
    for (status,) in statuses:
        count = db.query(Hackathon).filter(Hackathon.status == status).count()
        status_counts[status or "unknown"] = count

    return {"total_hackathons": total, "by_status": status_counts}
