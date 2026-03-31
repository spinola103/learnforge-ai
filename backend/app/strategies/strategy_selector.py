from app.strategies.nudge import generate_nudge
from app.strategies.breakdown import generate_breakdown
from app.strategies.socratic import generate_socratic
from app.strategies.analogy import generate_analogy

STRATEGY_MAP = {
    "arithmetic":    "nudge",
    "procedural":    "breakdown",
    "conceptual":    "analogy",
    "misconception": "socratic",
    "transfer":      "breakdown"
}


def select_strategy(mistake_type: str, mistake_history: list = None) -> str:
    base = STRATEGY_MAP.get(mistake_type, "breakdown")
    if not mistake_history:
        return base
    if base == "breakdown":
        failures = [m for m in mistake_history
                    if m["strategy_used"] == "breakdown"
                    and not m["student_improved"]]
        if len(failures) >= 3:
            return "socratic"
    if base == "socratic":
        failures = [m for m in mistake_history
                    if m["strategy_used"] == "socratic"
                    and not m["student_improved"]]
        if len(failures) >= 2:
            return "breakdown"
    return base


def run_strategy(
    strategy_name: str,
    problem: str,
    student_answer: str,
    concept: str,
    session_state: dict = None
) -> dict:
    if session_state is None:
        session_state = {}

    state = dict(session_state)

    if strategy_name == "nudge":
        message = generate_nudge(problem, student_answer, concept)
        return {"message": message, "session_state": state, "strategy": "nudge"}

    elif strategy_name == "breakdown":
        current_step = state.get("breakdown_step", 0)
        step_history = state.get("step_history", [])
        step_plan = state.get("step_plan", None)   # reuse cached plan
        is_retry = state.get("is_retry", False)

        result = generate_breakdown(
            problem=problem,
            student_answer=student_answer,
            concept=concept,
            current_step=current_step,
            step_history=step_history,
            step_plan=step_plan,
            is_retry=is_retry
        )

        # Cache the step plan in state
        state["step_plan"] = result["step_plan"]

        if result["validated"] and not result["is_retry"]:
            # Step passed — record it and advance
            updated_history = step_history + [{
                "step_index": current_step,
                "student_response": student_answer,
                "validated": True
            }]
            state["breakdown_step"] = result["step"]
            state["step_history"] = updated_history
            state["is_retry"] = False
        else:
            # Step failed — stay, mark retry
            state["is_retry"] = True

        state["breakdown_complete"] = result["is_final"] and result["validated"]
        state["total_steps"] = result["total_steps"]

        return {
            "message": result["message"],
            "session_state": state,
            "strategy": "breakdown"
        }

    elif strategy_name == "socratic":
        exchange_count = state.get("socratic_exchanges", 0)
        history = state.get("socratic_history", [])
        message = generate_socratic(
            problem, student_answer, concept, exchange_count, history
        )
        state["socratic_exchanges"] = exchange_count + 1
        state["socratic_history"] = history + [
            {"role": "assistant", "content": message}
        ]
        return {"message": message, "session_state": state, "strategy": "socratic"}

    elif strategy_name == "analogy":
        message = generate_analogy(problem, student_answer, concept)
        return {"message": message, "session_state": state, "strategy": "analogy"}

    else:
        return {
            "message": "Can you walk me through your reasoning step by step?",
            "session_state": state,
            "strategy": "fallback"
        }