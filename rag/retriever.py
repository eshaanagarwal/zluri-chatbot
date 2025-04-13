from typing import List, Dict
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from rag.embedder import search_index


def hybrid_retrieve(
    query: str,
    model,
    section_index,
    chunk_index,
    chunks: List[Dict],
    section_threshold: float = 0.65,
    top_k: int = 4,
) -> List[Dict]:
    """
    Hybrid retrieval:
    1. Embed query
    2. Try to match section titles (via section embeddings)
    3. If confident match, return those chunks
    4. Else fallback to chunk content search
    """
    query_embedding = model.encode([query], normalize_embeddings=True)[0]

    # Search section index 
    # add a BM25 retriever for section matching
    # section_index = BM25Retriever(chunks)

    section_scores, section_ids = section_index.search(
        query_embedding.reshape(1, -1), top_k
    )

    print(section_scores)
    print(section_ids)

    best_section_score = section_scores[0][0]
    best_section_id = section_ids[0][0]
    best_section_name = chunks[best_section_id]["section"]
    valid_section_ids = [s for s in section_ids[0] if s > section_threshold]

    if best_section_score >= section_threshold:
        print(
            f"📌 Matched section: {best_section_name} (score: {best_section_score:.2f})"
        )

        # need to add the hierarchy in text and not only just section name
        # get bm25 retriever for the section
        # Return all chunks from that section
        selected_chunks = [
            chunk for chunk in chunks if chunk["section"] in valid_section_ids
        ]
        return selected_chunks[:top_k]

    else:
        print("⚠️ No strong section match. Falling back to full content similarity.")
        # Fallback to content chunk similarity
        content_results = search_index(chunk_index, query_embedding, chunks, top_k)
        return content_results
