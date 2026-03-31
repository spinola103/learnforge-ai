import ollama


def generate_nudge(problem: str, student_answer: str, concept: str) -> str:
    """
    Generalised nudge for any arithmetic slip on any problem.
    Points to exactly where the calculation went wrong.
    """
    prompt = f"""A student made a small calculation error.

Problem: {problem}
Concept: {concept}
Student's answer: {student_answer}

Their method and approach are correct — it's just a small arithmetic slip.

Write exactly 2 sentences:
1. Confirm their approach/method is correct (be specific about what they did right)
2. Point to the ONE specific calculation step to recheck (name the exact step, not vague)

Rules:
- Do NOT give the correct answer
- Do NOT re-explain the concept
- Be specific: name the exact calculation (e.g., "check your multiplication of 0.15 × 200")
- Maximum 2 sentences"""

    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.1}
    )
    return response["message"]["content"].strip()