from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.student import Student, ConceptMastery, MistakeLog

router = APIRouter(prefix="/student", tags=["student"])

class CreateStudentRequest(BaseModel):
    name: str

@router.post("/create")
def create_student(req: CreateStudentRequest, db: Session = Depends(get_db)):
    student = Student(name=req.name)
    db.add(student)
    db.commit()
    db.refresh(student)
    return {"student_id": student.id, "name": student.name}

@router.get("/{student_id}/model")
def get_student_model(student_id: int, db: Session = Depends(get_db)):
    mastery = db.query(ConceptMastery).filter(
        ConceptMastery.student_id == student_id
    ).all()
    mistakes = db.query(MistakeLog).filter(
        MistakeLog.student_id == student_id
    ).order_by(MistakeLog.timestamp.desc()).limit(20).all()

    mistake_counts = {}
    for m in mistakes:
        mistake_counts[m.mistake_type] = mistake_counts.get(m.mistake_type, 0) + 1

    return {
        "student_id": student_id,
        "mastery": {m.concept: round(m.mastery_score, 1) for m in mastery},
        "mistake_profile": mistake_counts,
        "total_sessions": len(set(m.session_id for m in mistakes)),
        "total_mistakes": len(mistakes)
    }