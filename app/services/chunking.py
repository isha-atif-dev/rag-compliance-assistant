"""
Chunking service for the RAG pipeline.

Turns raw policy documents (data/*.txt) into a list of small, overlapping
text chunks that can later be embedded and searched. This is Phase 2 of
the RAG pipeline: Document -> [chunking] -> Embedding -> Storage -> Retrieval.
"""

from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_documents(folder: str = "data"):
    """
    Read every .txt file in the given folder.

    Returns a list of dicts like:
        {"source": "01_aml_policy.txt", "text": "<full file content>"}

    "source" is kept so that later, when we retrieve a chunk, we know
    exactly which original document it came from (needed for citations).
    """
    docs = []
    for file_path in Path(folder).glob("*.txt"):
        text = file_path.read_text(encoding="utf-8")
        docs.append({"source": file_path.name, "text": text})
    return docs

def extract_title(text: str) -> str:
    """
    Pull a short document title from the raw text, so it can be
    prepended to each chunk before embedding.

    Documents are formatted with the company name on line 1 and the
    actual title on line 2, e.g.:
        Meridian Financial Services Ltd
        ANTI-MONEY LAUNDERING (AML) POLICY
    We grab line 2. Falls back to line 1 if the file is shorter than expected.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) >= 2:
        return lines[1]
    return lines[0] if lines else "Untitled document"

def chunk_documents(docs, chunk_size=500, chunk_overlap=50):
    """
    Split each document into overlapping chunks.

    Each chunk carries two versions of its text:
      - "text": the raw chunk, used for display and citations
      - "embedding_text": the chunk prefixed with its document title,
        used only to generate the embedding. Many of our policies use
        near-identical generic phrasing ("must be reported within X
        business days"), so keeping the document's title attached to
        every one of its chunks, not just the first, helps retrieval
        actually distinguish which policy a chunk belongs to.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " "],
    )
    chunks = []
    for doc in docs:
        title = extract_title(doc["text"])
        pieces = splitter.split_text(doc["text"])
        for i, piece in enumerate(pieces):
            chunks.append({
                "source": doc["source"],
                "chunk_id": f"{doc['source']}::chunk{i}",
                "text": piece,
                "embedding_text": f"Document: {title}\n\n{piece}",
            })
    return chunks