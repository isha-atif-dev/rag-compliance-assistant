"""
Phase 6: Retrieval evaluation.

Runs every question in eval_questions.py through hybrid_search and
calculates Recall@5: the percentage of questions for which the
correct source document appears somewhere in the top 5 retrieved
chunks. This replaces eyeballing individual results with a real,
repeatable number.
"""

from app.services.retrieval import hybrid_search
from scripts.eval_questions import EVAL_QUESTIONS


def main():
    correct = 0
    failures = []

    for item in EVAL_QUESTIONS:
        question = item["question"]
        expected = item["expected_source"]

        results = hybrid_search(question, top_k=5)
        retrieved_sources = [r["source"] for r in results]

        if expected in retrieved_sources:
            correct += 1
        else:
            failures.append({
                "question": question,
                "expected": expected,
                "got": retrieved_sources,
            })

    total = len(EVAL_QUESTIONS)
    recall_at_5 = correct / total

    print(f"Recall@5: {correct}/{total} = {recall_at_5:.1%}\n")

    if failures:
        print("--- Missed questions ---")
        for f in failures:
            print(f"Q: {f['question']}")
            print(f"   Expected: {f['expected']}")
            print(f"   Got: {f['got']}")
            print()
    else:
        print("All questions passed.")


if __name__ == "__main__":
    main()