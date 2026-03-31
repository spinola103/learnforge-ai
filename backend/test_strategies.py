from app.classifier.mistake_classifier import classify_mistake
from app.strategies.strategy_selector import select_strategy, run_strategy

test_cases = [
    {
        "label": "Arithmetic Mistake → Nudge",
        "problem": "What is 15% of 200?",
        "correct": "30",
        "student": "31",
        "concept": "percentages"
    },
    {
        "label": "Procedural Mistake → Breakdown",
        "problem": "Solve for x: 2x + 6 = 14",
        "correct": "4",
        "student": "3",
        "concept": "linear_equations"
    },
    {
        "label": "Misconception → Socratic",
        "problem": "A train travels at 60km/h for 2.5 hours. How far does it travel?",
        "correct": "150",
        "student": "62.5",
        "concept": "distance_speed_time"
    },
    {
    "label": "Conceptual Mistake → Analogy",
    "problem": "Expand: 3(x + 4)",
    "correct": "3x + 12",
    "student": "3x + 4",
    "concept": "distributive_property"
}
]

print("=" * 65)
print("LEARNFORGE — FULL PIPELINE TEST (Classifier + Strategy)")
print("=" * 65)

for tc in test_cases:
    print(f"\n{'─' * 65}")
    print(f"TEST: {tc['label']}")
    print(f"Problem : {tc['problem']}")
    print(f"Student : {tc['student']}  |  Correct: {tc['correct']}")

    # Step 1: Classify
    mistake_type = classify_mistake(
        tc["problem"], tc["correct"], tc["student"], tc["concept"]
    )
    print(f"Classified as: {mistake_type.upper()}")

    # Step 2: Select strategy
    strategy = select_strategy(mistake_type)
    print(f"Strategy selected: {strategy.upper()}")

    # Step 3: Run strategy
    result = run_strategy(strategy, tc["problem"], tc["student"], tc["concept"])
    print(f"\n📚 LearnForge Response:\n{result['message']}")

print(f"\n{'=' * 65}")
print("Pipeline test complete.")
print("=" * 65)