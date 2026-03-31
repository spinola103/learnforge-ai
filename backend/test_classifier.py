from app.classifier.mistake_classifier import classify_mistake

test_cases = [
    {
        "problem": "Solve for x: 2x + 6 = 14",
        "correct": "4",
        "student": "3",
        "concept": "linear_equations",
        "expected": "procedural"
    },
    {
        "problem": "What is 15% of 200?",
        "correct": "30",
        "student": "31",
        "concept": "percentages",
        "expected": "arithmetic"   # very close numerically
    },
    {
        "problem": "Simplify: (x^2 - 4) / (x - 2)",
        "correct": "x + 2",
        "student": "x - 2",
        "concept": "factoring",
        "expected": "conceptual"
    },
    {
        "problem": "A train travels 60km/h for 2.5 hours. How far?",
        "correct": "150",
        "student": "62.5",
        "concept": "distance_speed_time",
        "expected": "misconception"  # student likely added instead of multiplied
    },
    {
        "problem": "Expand: 3(x + 4)",
        "correct": "3x + 12",
        "student": "3x + 4",
        "concept": "distributive_property",
        "expected": "procedural"
    }
]

print("=" * 60)
print("LEARNFORGE MISTAKE CLASSIFIER — TEST RUN")
print("=" * 60)

passed = 0
for i, tc in enumerate(test_cases):
    result = classify_mistake(
        tc["problem"],
        tc["correct"],
        tc["student"],
        tc["concept"]
    )
    status = "✓ PASS" if result == tc["expected"] else f"✗ FAIL (expected {tc['expected']})"
    if result == tc["expected"]:
        passed += 1
    print(f"\nTest {i+1}: {tc['problem'][:45]}...")
    print(f"  Student answered: {tc['student']}  |  Correct: {tc['correct']}")
    print(f"  Classified as: {result.upper():15} {status}")

print("\n" + "=" * 60)
print(f"Results: {passed}/{len(test_cases)} passed")
print("=" * 60)