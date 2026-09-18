"""
Manual sanity check for hybrid retrieval (vector + keyword, merged via RRF).
"""

from app.services.retrieval import hybrid_search

question = "What is the timeline for reporting suspicious activity?"
results = hybrid_search(question, top_k=5)

print(f"Question: {question}\n")
for i, r in enumerate(results, start=1):
    marker = " <-- SAR doc" if "sar" in r["source"].lower() else ""
    print(f"{i}. {r['source']}{marker}")
    print(f"   {r['text'][:150]}...")