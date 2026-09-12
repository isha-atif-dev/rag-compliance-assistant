"""
Generation service for the RAG pipeline.

Takes retrieved chunks (from retrieval.py) and a user's question, builds
a grounded prompt instructing Claude to answer using only the provided
evidence, and returns the answer with citations back to source documents.

This is Phase 4: Question -> Retrieval (done) -> [Generation] -> Answer + citations.
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a compliance assistant for Meridian Financial Services Ltd.

Answer the user's question using ONLY the policy excerpts provided below.
Do not use any outside knowledge, even if you know the general topic.

Rules:
- If the excerpts don't contain enough information to answer, say so clearly. Do not guess.
- After your answer, list the specific source documents you used, exactly as given in the excerpt labels.
- Be concise and precise, this is a compliance context, accuracy matters more than length.
"""


def build_context(chunks):
    """
    Format retrieved chunks into a labelled block of evidence the LLM can
    reference, e.g.:
        [Source: 12_sar_procedure.txt]
        <chunk text>
    """
    blocks = []
    for chunk in chunks:
        blocks.append(f"[Source: {chunk['source']}]\n{chunk['text']}")
    return "\n\n---\n\n".join(blocks)


def generate_answer(question: str, chunks: list) -> dict:
    """
    Calls Claude with the question and retrieved chunks, grounded via the
    system prompt above. Returns the answer text plus the list of sources
    that were made available (not necessarily all cited, but this is what
    the model had access to, useful for showing "based on" in the UI).
    """
    context = build_context(chunks)

    user_message = f"""Policy excerpts:

{context}

---

Question: {question}"""

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    answer_text = response.content[0].text
    sources_available = sorted(set(c["source"] for c in chunks))

    return {
        "answer": answer_text,
        "sources_available": sources_available,
    }