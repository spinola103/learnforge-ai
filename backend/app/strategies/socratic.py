import ollama


def generate_socratic(
    problem: str,
    student_answer: str,
    concept: str,
    exchange_count: int = 0,
    conversation_history: list = None
) -> str:
    if conversation_history is None:
        conversation_history = []

    if exchange_count == 0:
        messages = [{
            "role": "user",
            "content": f"""You are a Socratic math tutor. A student has a misconception.

Problem: {problem}
Student's wrong answer: {student_answer}
Concept: {concept}

The student believes their answer is correct. Ask ONE short question that 
leads them to question their own reasoning by testing a simpler case.

Rules:
- ONE question only, 1-2 sentences max
- Do NOT say "that's wrong" or anything negative
- Do NOT give the correct answer or hint at it
- The question should be something they can easily verify themselves"""
        }]

    elif exchange_count == 1:
        messages = [
            {
                "role": "user",
                "content": f"""You are a Socratic math tutor continuing a dialogue.
Original problem: {problem}
Concept: {concept}

The student responded. Push them one step closer to discovering the flaw.
Ask ONE more short probing question (1-2 sentences). No answer yet."""
            }
        ] + conversation_history

    else:
        messages = [
            {
                "role": "user",
                "content": f"""You are a Socratic math tutor wrapping up.
Original problem: {problem}
Concept: {concept}

Now:
1. One sentence confirming what the student has discovered
2. Briefly explain the correct concept (2 sentences max)
3. Ask them to solve the original problem now

Be warm. Be brief."""
            }
        ] + conversation_history

    response = ollama.chat(
        model="mistral",
        messages=messages,
        options={"temperature": 0.4}
    )
    return response["message"]["content"].strip()