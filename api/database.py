from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    JSON,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Use SQLite by default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./palmer.db")

# SQLite needs check_same_thread=False
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Hackathon(Base):
    __tablename__ = "hackathons"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)

    # Basic Info
    title = Column(String, index=True)
    tagline = Column(Text)
    status = Column(String, index=True)

    # Dates
    start_date = Column(String)
    end_date = Column(String)
    submission_deadline = Column(String)

    # Location
    location = Column(String, index=True)
    visibility = Column(String)

    # Participation
    participants_count = Column(Integer, default=0)

    # Organizer
    organizer = Column(String)

    # Rich Data (stored as JSON)
    prizes = Column(JSON)
    tags = Column(JSON)
    eligibility = Column(JSON)
    sponsors = Column(JSON)
    judges = Column(JSON)
    judging_criteria = Column(JSON)

    # Long Text
    description = Column(Text)
    requirements = Column(Text)

    # Metadata
    scraped_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "tagline": self.tagline,
            "status": self.status,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "submission_deadline": self.submission_deadline,
            "location": self.location,
            "visibility": self.visibility,
            "participants_count": self.participants_count,
            "organizer": self.organizer,
            "prizes": self.prizes,
            "tags": self.tags,
            "eligibility": self.eligibility,
            "sponsors": self.sponsors,
            "judges": self.judges,
            "judging_criteria": self.judging_criteria,
            "description": self.description,
            "requirements": self.requirements,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


def init_db():
    """Initialize the database"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
