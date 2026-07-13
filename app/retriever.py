"""Retriever: load docs, embed them, index in ChromaDB, and return top-k chunks.

Chunking choice: one chunk per markdown heading section (split on lines starting
with '#'). The PlanFlow docs are written so each section is a self-contained rule,
so heading-based chunks keep a whole rule together instead of cutting it mid-thought.
This is the simplest split that respects the document structure.
"""

import chromadb
from chromadb.utils import embedding_functions

from app import config

_COLLECTION = None


def _split_into_chunks(text: str) -> list[str]:
    """Split markdown into chunks, one per heading section."""
    chunks, current = [], []
    for line in text.splitlines():
        if line.startswith("#") and current:
            chunks.append("\n".join(current).strip())
            current = []
        current.append(line)
    if current:
        chunks.append("\n".join(current).strip())
    return [c for c in chunks if c]


def _build_collection():
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=config.EMBEDDING_MODEL
    )
    client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    collection = client.get_or_create_collection(
        name="planflow_docs", embedding_function=embed_fn
    )

    if collection.count() > 0:
        return collection  # already indexed

    ids, documents, metadatas = [], [], []
    for doc_path in sorted(config.DOCS_DIR.glob("*.md")):
        for i, chunk in enumerate(_split_into_chunks(doc_path.read_text(encoding="utf-8"))):
            ids.append(f"{doc_path.stem}-{i}")
            documents.append(chunk)
            metadatas.append({"source": doc_path.name})
    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    return collection


def retrieve(query: str, k: int = 3) -> list[str]:
    """Return the k most relevant doc chunks for a query."""
    global _COLLECTION
    if _COLLECTION is None:
        _COLLECTION = _build_collection()
    result = _COLLECTION.query(query_texts=[query], n_results=k)
    return result["documents"][0]
