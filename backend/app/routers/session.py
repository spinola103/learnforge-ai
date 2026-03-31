from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.database import get_db
from app.session_manager import start_session, process_response, end_session

router = APIRouter(prefix="/session", tags=["session"])

class StartRequest(BaseModel):
    student_id: int

class RespondRequest(BaseModel):
    session_id: str
    student_answer: str
    session_state: Optional[Dict[str, Any]] = None

@router.post("/start")
def session_start(req: StartRequest, db: Session = Depends(get_db)):
    return start_session(req.student_id, db)

@router.post("/respond")
def session_respond(req: RespondRequest, db: Session = Depends(get_db)):
    return process_response(req.session_id, req.student_answer, db, req.session_state)

@router.get("/end/{session_id}")
def session_end(session_id: str, db: Session = Depends(get_db)):
    return end_session(session_id, db)