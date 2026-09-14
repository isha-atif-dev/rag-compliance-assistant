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


def _build_citations(chunks):
    """
    Builds a deduplicated list of {source, snippet} for display in the UI,
    one entry per unique source document among the retrieved chunks, using
    the first chunk seen for that source as its representative snippet.
    """
    seen = set()
    citations = []
    for c in chunks:
        if c["source"] in seen:
            continue
        seen.add(c["source"])
        snippet = " ".join(c["text"].split())  # collapse newlines/whitespace
        if len(snippet) > 160:
            snippet = snippet[:160].rsplit(" ", 1)[0] + "..."
        citations.append({"source": c["source"], "snippet": snippet})
    return citations


def generate_answer(question: str, chunks: list) -> dict:
    """
    Calls Claude with the question and retrieved chunks, grounded via the
    system prompt above. Returns the answer, the list of source filenames
    available, and a richer citations list (source + snippet) for the UI.
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

    # Some responses may include a "thinking" block before the actual answer,
# so find the text block explicitly instead of assuming it's always first.
    answer_text = next(
        (block.text for block in response.content if block.type == "text"),
        None,
    )
    if answer_text is None:
        raise ValueError("No text content found in Claude's response")
    sources_available = sorted(set(c["source"] for c in chunks))
    citations = _build_citations(chunks)

    return {
        "answer": answer_text,
        "sources_available": sources_available,
        "citations": citations,
    }