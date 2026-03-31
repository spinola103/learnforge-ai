import json
import uuid
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from app.models.student import ConceptMastery, MistakeLog
from app.classifier.mistake_classifier import classify_mistake
from app.strategies.strategy_selector import select_strategy, run_strategy

DOMAIN_PATH = Path(__file__).parent / "domains" / "algebra.json"
with open(DOMAIN_PATH) as f:
    DOMAIN = json.load(f)

SESSIONS = {}


def get_student_mastery(db: Session, student_id: int) -> dict:
    records = db.query(ConceptMastery).filter(
        ConceptMastery.student_id == student_id
    ).all()
    return {r.concept: r.mastery_score for r in records}


def get_mistake_history(db: Session, student_id: int) -> list:
    records = db.query(MistakeLog).filter(
        MistakeLog.student_id == student_id
    ).order_by(MistakeLog.timestamp.desc()).limit(10).all()
    return [
        {
            "concept": r.concept,
            "mistake_type": r.mistake_type,
            "strategy_used": r.strategy_used,
            "student_improved": r.student_improved
        }
        for r in records
    ]


def select_next_problem(student_id: int, db: Session, sess: dict = None) -> dict:
    mastery = get_student_mastery(db, student_id)
    valid_concepts = {p["concept"] for p in DOMAIN["problems"]}
    concepts = [c for c in DOMAIN["concepts"] if c in valid_concepts]
    weakest = min(concepts, key=lambda c: mastery.get(c, 50))
    candidates = [p for p in DOMAIN["problems"] if p["concept"] == weakest]

    if sess:
        asked = set(sess.get("asked_problems", []))
        fresh = [p for p in candidates if p["id"] not in asked]
        if fresh:
            candidates = fresh

    if not candidates:
        candidates = DOMAIN["problems"]

    return sorted(candidates, key=lambda p: p["difficulty"])[0]


def start_session(student_id: int, db: Session) -> dict:
    session_id = str(uuid.uuid4())[:8]
    problem = select_next_problem(student_id, db)

    SESSIONS[session_id] = {
        "student_id": student_id,
        "current_problem": problem,
        "scaffold_depth": 0,
        "strategy": None,
        "mistake_type": None,
        "mode": "new_attempt",
        "mistakes_this_session": [],
        "asked_problems": [problem["id"]],
        "start_time": datetime.utcnow().isoformat()
    }

    return {
        "session_id": session_id,
        "message": f"Let's work on {problem['concept'].replace('_', ' ')}.",
        "problem": problem["prompt"],
        "topic": DOMAIN["topic"],
        "session_state": {}
    }


def check_answer(correct: str, student: str) -> bool:
    correct_clean = correct.strip().lower().replace(" ", "")
    student_clean = student.strip().lower().replace(" ", "")
    if correct_clean == student_clean:
        return True
    try:
        return abs(float(correct_clean) - float(student_clean)) < 0.01
    except ValueError:
        return False


def update_mastery(db: Session, student_id: int, concept: str, correct: bool):
    record = db.query(ConceptMastery).filter(
        ConceptMastery.student_id == student_id,
        ConceptMastery.concept == concept
    ).first()
    if not record:
        record = ConceptMastery(
            student_id=student_id,
            topic=DOMAIN["topic"],
            concept=concept,
            mastery_score=50.0
        )
        db.add(record)
    delta = 5.0 if correct else -3.0
    record.mastery_score = max(0, min(100, record.mastery_score + delta))
    record.last_updated = datetime.utcnow()
    db.commit()


def process_response(
    session_id: str,
    student_answer: str,
    db: Session,
    client_session_state: dict = None
) -> dict:
    if session_id not in SESSIONS:
        return {"error": "Session not found. Start a new session."}

    sess = SESSIONS[session_id]
    problem = sess["current_problem"]
    student_id = sess["student_id"]
    working_state = client_session_state if client_session_state else {}

    # ── CORRECT FINAL ANSWER ──────────────────────────────────────
    if check_answer(problem["correct_answer"], student_answer):
        update_mastery(db, student_id, problem["concept"], correct=True)

        if sess["mistake_type"] and sess["mistakes_this_session"]:
            last_log = db.query(MistakeLog).filter(
                MistakeLog.id == sess["mistakes_this_session"][-1]
            ).first()
            if last_log:
                last_log.student_improved = True
                db.commit()

        next_problem = select_next_problem(student_id, db, sess)
        sess["asked_problems"] = sess.get("asked_problems", []) + [next_problem["id"]]
        sess["current_problem"] = next_problem
        sess["scaffold_depth"] = 0
        sess["strategy"] = None
        sess["mistake_type"] = None
        sess["mode"] = "new_attempt"

        return {
            "correct": True,
            "message": "Correct! Well done working through that.",
            "next_problem": next_problem["prompt"],
            "concept": next_problem["concept"].replace("_", " "),
            "scaffold_depth": 0,
            "session_state": {}
        }

    # ── NO-ANSWER-FIRST PROTOCOL ──────────────────────────────────
    answer_keywords = ["what is the answer", "tell me the answer",
                       "just give me", "i give up", "answer please"]
    if any(kw in student_answer.lower() for kw in answer_keywords):
        if sess["scaffold_depth"] < 2:
            return {
                "correct": False,
                "message": (
                    f"You're closer than you think! Let's go through "
                    f"{2 - sess['scaffold_depth']} more step(s) together first."
                ),
                "scaffold_depth": sess["scaffold_depth"],
                "session_state": working_state,
                "strategy": sess.get("strategy"),
                "mistake_type": sess.get("mistake_type")
            }

    # ── FIRST WRONG ATTEMPT — classify and start strategy ────────
    if sess["mode"] == "new_attempt":
        mistake_type = classify_mistake(
            problem["prompt"],
            problem["correct_answer"],
            student_answer,
            problem["concept"]
        )
        history = get_mistake_history(db, student_id)
        strategy = select_strategy(mistake_type, history)

        sess["mistake_type"] = mistake_type
        sess["strategy"] = strategy
        sess["mode"] = "in_strategy"

        log = MistakeLog(
            student_id=student_id,
            session_id=session_id,
            concept=problem["concept"],
            mistake_type=mistake_type,
            strategy_used=strategy,
            student_improved=False
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        sess["mistakes_this_session"].append(log.id)
        update_mastery(db, student_id, problem["concept"], correct=False)

        # ── KEY FIX: For breakdown, start with EMPTY step_history ──
        # The original wrong answer (e.g. "12") triggered breakdown.
        # It is NOT a step response — don't record it as step history.
        # working_state stays clean: { } so step 1 shows fresh.
        if strategy == "breakdown":
            working_state = {"step_history": [], "breakdown_step": 0}

    # Nudge escalation — after one nudge that didn't help
    if sess["strategy"] == "nudge" and sess["scaffold_depth"] >= 1:
        sess["strategy"] = "breakdown"
        # Fresh breakdown state — nudge answer also should NOT appear in step history
        working_state = {"step_history": [], "breakdown_step": 0}

    # ── IN STRATEGY MODE ─────────────────────────────────────────
    # For breakdown: when student responds to a step,
    # mark their response as belonging to the current step index
    if sess["strategy"] == "breakdown" and sess["scaffold_depth"] > 0:
        current_step_index = working_state.get("breakdown_step", 0)
        existing_history = working_state.get("step_history", [])

        # Only record if this step isn't already in history
        already_recorded = any(
            h.get("step_index") == current_step_index
            for h in existing_history
        )

        if not already_recorded and current_step_index >= 0:
            # Student is responding to current_step_index
            # Add their response so breakdown.py can validate it
            working_state["step_history"] = existing_history + [{
                "step_index": current_step_index,
                "student_response": student_answer,
                "validated": False   # breakdown.py will re-validate
            }]

    # Run strategy
    result = run_strategy(
        sess["strategy"],
        problem["prompt"],
        student_answer,
        problem["concept"],
        working_state
    )

    # Only increment scaffold depth if step was validated (not a retry)
    is_retry = result["session_state"].get("is_retry", False)
    if not is_retry:
        sess["scaffold_depth"] += 1

    return {
        "correct": False,
        "mistake_type": sess["mistake_type"],
        "strategy": sess["strategy"],
        "message": result["message"],
        "scaffold_depth": sess["scaffold_depth"],
        "session_state": result["session_state"],
        "is_retry": is_retry
    }


def end_session(session_id: str, db: Session) -> dict:
    if session_id not in SESSIONS:
        return {"error": "Session not found."}

    sess = SESSIONS[session_id]
    student_id = sess["student_id"]

    logs = db.query(MistakeLog).filter(
        MistakeLog.id.in_(sess["mistakes_this_session"])
    ).all()

    mistake_summary = {}
    for log in logs:
        t = log.mistake_type
        mistake_summary[t] = mistake_summary.get(t, 0) + 1

    mastery = get_student_mastery(db, student_id)
    weakest = min(mastery, key=mastery.get) if mastery else "general algebra"
    del SESSIONS[session_id]

    return {
        "session_id": session_id,
        "total_mistakes": len(logs),
        "improved": sum(1 for l in logs if l.student_improved),
        "mistake_breakdown": mistake_summary,
        "mastery_snapshot": mastery,
        "recommendation": f"Focus on {weakest.replace('_', ' ')} before your next session.",
        "message": build_recap_message(logs, mistake_summary, weakest)
    }


def build_recap_message(logs, mistake_summary, weakest) -> str:
    if not logs:
        return "Great session — no mistakes recorded!"
    lines = ["Here's what happened this session:\n"]
    for mtype, count in mistake_summary.items():
        improved = sum(1 for l in logs
                       if l.mistake_type == mtype and l.student_improved)
        lines.append(
            f"• {count} {mtype} mistake(s) — "
            f"{'corrected after guidance ✓' if improved else 'still needs work'}"
        )
    lines.append(
        f"\nRecommended focus: {weakest.replace('_', ' ')}. "
        f"Practice 2–3 more problems before your next session."
    )
    return "\n".join(lines)

