import ollama

def generate_analogy(problem: str, student_answer: str, concept: str) -> str:
    prompt = f"""You are a math tutor. A student has a conceptual misunderstanding.

Problem: {problem}
Student's wrong answer: {student_answer}
Concept: {concept}

Their error is not a calculation slip — they misunderstand what the concept means.

Your job:
1. Do NOT correct them directly
2. Explain the concept using a completely different real-world analogy 
   (shopping, cooking, sports — anything concrete and relatable)
3. After the analogy, ask them to re-attempt the problem with this new understanding

Rules:
- Keep the analogy simple and short (3-4 sentences)
- End with a question inviting them to try again
- Do NOT give the answer"""

    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.5}
    )
    return response["message"]["content"].strip()