"""
Sanity-check script for embeddings (Phase 2).

Proves the core idea before using it for real: sentences with similar
meaning should produce embeddings that are numerically close together,
even if they share almost no words. Sentences with unrelated meaning
should be numerically far apart.
"""

from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

sentences = [
    "How do I report suspicious activity?",       # similar meaning to sentence 2
    "What are the steps for filing a SAR?",        # similar meaning to sentence 1
    "What time does the office close on Fridays?", # unrelated meaning
]

embeddings = model.encode(sentences)

print("Similarity: SAR question 1 vs SAR question 2 (expect HIGH)")
print(util.cos_sim(embeddings[0], embeddings[1]).item())

print("\nSimilarity: SAR question vs unrelated office hours question (expect LOW)")
print(util.cos_sim(embeddings[0], embeddings[2]).item())