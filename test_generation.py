"""
Manual sanity check for Phase 4: full pipeline, question to grounded answer.
"""

from app.services.retrieval import hybrid_search
from app.services.generation import generate_answer

question = "What is the timeline for reporting suspicious activity?"

chunks = hybrid_search(question, top_k=5)
result = generate_answer(question, chunks)

print(f"Question: {question}\n")
print("Answer:")
print(result["answer"])
print("\nSources available:", result["sources_available"])