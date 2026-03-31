from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ConceptMastery(Base):
    __tablename__ = "concept_mastery"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, nullable=False)
    topic = Column(String, nullable=False)
    concept = Column(String, nullable=False)
    mastery_score = Column(Float, default=50.0)   # starts neutral at 50
    last_updated = Column(DateTime, default=datetime.utcnow)

class MistakeLog(Base):
    __tablename__ = "mistake_log"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, nullable=False)
    session_id = Column(String, nullable=False)
    concept = Column(String, nullable=False)
    mistake_type = Column(String, nullable=False)
    strategy_used = Column(String, nullable=False)
    student_improved = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    