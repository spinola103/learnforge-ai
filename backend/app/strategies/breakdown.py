import ollama
import json
import random

ENCOURAGEMENTS = [
    "Nice work! ✓",
    "That's right! ✓",
    "Exactly! ✓",
    "Well done! ✓",
    "Correct! ✓",
    "Perfect — keep going! ✓"
]

RETRY_PHRASES = [
    "Not quite — try again.",
    "Check your working and try once more.",
    "That's not right yet — give it another go.",
    "Hmm, look at that step again."
]


def generate_step_plan(problem: str, concept: str) -> list:
    """
    Generate a concrete, mathematical step plan for any problem.
    Steps must produce verifiable intermediate results — not meta-instructions.
    """
    prompt = f"""You are an expert math teacher breaking down a problem for a student.

Problem: {problem}
Concept: {concept}

Create a step-by-step solution where each step:
- Performs ONE concrete mathematical action
- Produces a specific mathematical result the student can write down
- Builds directly on the previous step

Respond with ONLY a JSON array. No markdown, no explanation, just the array:
[
  {{
    "instruction": "Subtract 6 from both sides of 2x + 6 = 14",
    "expected_result": "2x = 8",
    "what_to_ask": "What equation do you get after subtracting 6 from both sides?"
  }},
  {{
    "instruction": "Divide both sides by 2 to isolate x",
    "expected_result": "x = 4",
    "what_to_ask": "Now divide both sides by 2. What is x?"
  }}
]

CRITICAL RULES:
- Each "instruction" must name the EXACT mathematical operation (e.g., "Subtract 6", "Divide by 2", "Multiply 3 by x")
- Each "expected_result" must be the actual mathematical expression/number the student should produce
- Each "what_to_ask" is one question asking the student to perform that specific step
- 2-3 steps for simple problems, 3-4 for complex ones
- NEVER use vague instructions like "identify", "figure out", "think about", "simplify generally"
- The steps must SOLVE the problem when followed in order"""

    try:
        response = ollama.chat(
            model="mistral",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.1}
        )
        raw = response["message"]["content"].strip()
        raw = raw.replace("```json", "").replace("```", "").strip()

        # Extract JSON array
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start != -1 and end > start:
            raw = raw[start:end]

        steps = json.loads(raw)

        validated = []
        for s in steps:
            if all(k in s for k in ["instruction", "expected_result", "what_to_ask"]):
                validated.append({
                    "instruction": str(s["instruction"]).strip(),
                    "expected_result": str(s["expected_result"]).strip(),
                    "what_to_ask": str(s["what_to_ask"]).strip()
                })
        if validated:
            return validated

    except Exception as e:
        print(f"[StepPlan Error] {e} — using fallback")

    # Fallback: ask LLM to just solve it step by step in plain text then parse
    return _fallback_step_plan(problem, concept)


def _fallback_step_plan(problem: str, concept: str) -> list:
    """Fallback if JSON parsing fails — simpler prompt."""
    prompt = f"""Solve this problem step by step: {problem}

Write exactly 3 lines, each line is one step:
STEP1: [what to do] | [result]
STEP2: [what to do] | [result]  
STEP3: [what to do] | [result]"""

    try:
        response = ollama.chat(
            model="mistral",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.0}
        )
        raw = response["message"]["content"].strip()
        steps = []
        for line in raw.split("\n"):
            if "|" in line and ("STEP" in line.upper() or line.strip().startswith("-")):
                parts = line.split("|")
                if len(parts) >= 2:
                    instruction = parts[0].replace("STEP1:", "").replace("STEP2:", "").replace("STEP3:", "").strip()
                    expected = parts[1].strip()
                    steps.append({
                        "instruction": instruction,
                        "expected_result": expected,
                        "what_to_ask": f"What do you get when you {instruction.lower()}?"
                    })
        if steps:
            return steps
    except Exception:
        pass

    return [
        {
            "instruction": f"Apply the first step to solve: {problem}",
            "expected_result": "intermediate result",
            "what_to_ask": "Show your working for the first step."
        },
        {
            "instruction": "Complete the calculation",
            "expected_result": "final answer",
            "what_to_ask": "What is your final answer?"
        }
    ]


def validate_step(student_response: str, step: dict, problem: str) -> dict:
    """
    Strict validation: checks if student's response is mathematically correct
    for the specific step — not just non-empty.
    """
    prompt = f"""You are a strict math teacher checking one step of a student's work.

Original problem: {problem}
Current step instruction: {step['instruction']}
Expected result for this step: {step['expected_result']}
Student's response: {student_response}

Question: Is the student's response mathematically correct for this step?

Rules for judging:
- The student must have performed the correct mathematical operation
- Minor notation differences are OK (e.g., "x=4" vs "x = 4")
- Completely wrong answers, random text, or skipped steps are NOT OK
- If expected_result is "2x = 8" and student wrote "2x = 8" or "2x=8", that's VALID
- If expected_result is "x = 4" and student wrote "4" or "x=4", that's VALID
- If student wrote something unrelated or wrong, that's INVALID

Respond with ONLY this JSON (no other text):
{{"valid": true, "hint": ""}}
OR
{{"valid": false, "hint": "One specific hint about what the student should do, without giving the answer"}}"""

    try:
        response = ollama.chat(
            model="mistral",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.0}
        )
        raw = response["message"]["content"].strip()
        raw = raw.replace("```json", "").replace("```", "").strip()

        # Extract JSON
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            raw = raw[start:end]

        result = json.loads(raw)
        is_valid = bool(result.get("valid", False))
        hint = str(result.get("hint", "")).strip()

        return {
            "valid": is_valid,
            "feedback": random.choice(ENCOURAGEMENTS) if is_valid else random.choice(RETRY_PHRASES),
            "hint": hint if hint else step.get("what_to_ask", "Try again.")
        }

    except Exception as e:
        print(f"[Validation Error] {e}")
        # Conservative fallback — check basic non-triviality
        is_trivial = len(student_response.strip()) < 2 or student_response.strip().lower() in [
            "i don't know", "idk", "?", "help", "no", "yes"
        ]
        return {
            "valid": not is_trivial,
            "feedback": random.choice(ENCOURAGEMENTS) if not is_trivial else random.choice(RETRY_PHRASES),
            "hint": step.get("what_to_ask", "Show your mathematical working.")
        }


def generate_breakdown(
    problem: str,
    student_answer: str,
    concept: str,
    current_step: int = 0,
    step_history: list = None,
    step_plan: list = None,
    is_retry: bool = False
) -> dict:
    """
    Fully generalised breakdown engine.
    Works for any problem — algebra, geometry, coding, language, etc.
    """

    # Generate or reuse step plan
    if not step_plan:
        step_plan = generate_step_plan(problem, concept)

    total_steps = len(step_plan)
    current_step = min(current_step, total_steps - 1)
    step = step_plan[current_step]
    is_final = current_step == total_steps - 1

    # Validate current step if student is responding to it
    validation = None
    if step_history and len(step_history) > 0:
        last = step_history[-1]
        if last.get("step_index") == current_step:
            validation = validate_step(student_answer, step, problem)

            if not validation["valid"]:
                # Stay on same step — show targeted hint
                return {
                    "message": (
                        f"{validation['feedback']}\n\n"
                        f"{'🎯 Final step' if is_final else f'Step {current_step + 1} of {total_steps}'}: "
                        f"{step['instruction']}\n\n"
                        f"💡 {validation['hint']}"
                    ),
                    "step": current_step,
                    "total_steps": total_steps,
                    "is_final": is_final,
                    "is_retry": True,
                    "validated": False,
                    "step_plan": step_plan
                }

    # Build summary of completed steps
    context_lines = []
    if step_history:
        completed = [h for h in step_history if h.get("validated", True)]
        if completed:
            context_lines.append("Done so far:")
            for h in completed:
                idx = h.get("step_index", 0)
                if idx < len(step_plan):
                    context_lines.append(
                        f"  ✓ {step_plan[idx]['instruction']} → {h['student_response']}"
                    )

    context = "\n".join(context_lines) + "\n\n" if context_lines else ""
    encouragement = f"{validation['feedback']}\n\n" if (validation and validation["valid"]) else ""
    step_label = "🎯 Final step" if is_final else f"Step {current_step + 1} of {total_steps}"

    # The key: show the concrete step + what to ask
    message = (
        f"{encouragement}"
        f"{context}"
        f"{step_label}: {step['instruction']}\n\n"
        f"→ {step['what_to_ask']}"
    )

    return {
        "message": message,
        "step": current_step + 1,
        "total_steps": total_steps,
        "is_final": is_final,
        "is_retry": False,
        "validated": True,
        "step_plan": step_plan
    }