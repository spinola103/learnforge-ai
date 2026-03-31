import ollama

VALID_TYPES = {"conceptual", "procedural", "arithmetic", "misconception", "transfer"}

def is_close_numerically(correct: str, student: str, tolerance: float = 0.05) -> bool:
    try:
        c = float(correct.strip())
        s = float(student.strip())
        if c == 0:
            return abs(s) < 0.01
        return abs(c - s) / abs(c) <= tolerance
    except ValueError:
        return False

def build_prompt(problem: str, correct_answer: str, student_answer: str, concept: str) -> str:
    return f"""You are an expert educator. Classify a student's mistake into exactly one category.

CATEGORY DEFINITIONS WITH EXAMPLES:

conceptual — student misunderstands what the concept means or how it works fundamentally
  Example: Problem: "Simplify (x²-4)/(x-2)", Correct: "x+2", Student: "x-2"
  Why conceptual: Student doesn't understand that (x²-4) factors as (x+2)(x-2)

procedural — student understands the concept but executes the wrong steps
  Example: Problem: "Solve 2x+6=14", Correct: "4", Student: "3"  
  Why procedural: Student subtracted 6 correctly to get 2x=8, then divided wrongly

arithmetic — correct method and understanding, pure calculation slip
  Example: Problem: "15% of 200", Correct: "30", Student: "31"
  Why arithmetic: Method is right, just a small calculation error

misconception — student holds a wrong belief they think is correct, leading to systematic error
  Example: Problem: "Train at 60km/h for 2.5hrs, distance?", Correct: "150", Student: "62.5"
  Why misconception: Student believes distance = speed + time (addition), not multiplication

transfer — student solved the standard form but fails when context changes slightly
  Example: Problem: "If 3x=12 find x, now if 3y+1=13 find y", Correct: "4", Student: "13/3"
  Why transfer: Student solved 3x=12 correctly but cannot apply same logic with offset

NOW CLASSIFY THIS:
Problem: {problem}
Correct answer: {correct_answer}
Student's answer: {student_answer}
Concept: {concept}

Think step by step silently, then output ONLY the category name.
Your response must be a single word from: conceptual, procedural, arithmetic, misconception, transfer"""

def classify_mistake(
    problem: str,
    correct_answer: str,
    student_answer: str,
    concept: str
) -> str:
    # Layer 1 — fast arithmetic pre-filter
    if is_close_numerically(correct_answer, student_answer):
        return "arithmetic"

    # Layer 2 — LLM with few-shot prompt
    prompt = build_prompt(problem, correct_answer, student_answer, concept)

    try:
        response = ollama.chat(
            model="mistral",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.1}   # low temperature = more deterministic
        )
        result = response["message"]["content"].strip().lower()

        # Clean up — sometimes LLM adds punctuation or extra words
        result = result.replace(".", "").replace(",", "").split()[0]

        if result in VALID_TYPES:
            return result

        # Substring fallback
        for t in VALID_TYPES:
            if t in result:
                return t

        return "conceptual"

    except Exception as e:
        print(f"[Classifier Error] {e}")
        return "conceptual"