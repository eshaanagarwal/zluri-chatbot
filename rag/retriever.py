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
    top_k: int = 5,
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

    # Retrieve top_k section scores and section IDs
    section_scores, section_ids = section_index.search(
        query_embedding.reshape(1, -1), top_k
    )

    print("Section Scores:", section_scores)
    print("Section IDs:", section_ids)

    best_section_score = section_scores[0][0]
    best_section_id = section_ids[0][0]
    best_section_name = chunks[best_section_id]["section"]

    # Determine if all returned section scores are above the threshold
    min_section_score = min(section_scores[0])

    if min_section_score > section_threshold:
        # All retrieved sections have strong scores.
        print(f"📌 Matched section hierarchy: {best_section_name} (top score: {best_section_score:.2f})")
        
        # NOTE: Here, you can extend the text to include a full hierarchical representation of the section.
        selected_chunks = [
            chunk for chunk in chunks if chunk["id"] in section_ids[0]
        ]

        # print(selected_chunks)
        return selected_chunks[:top_k]

    else:
        # Fusion logic: Combine section-based and full content-based retrieval.
        
        # First, select sections that meet the threshold.
        valid_section_ids = [
            section_ids[0][i] for i, score in enumerate(section_scores[0])
            if score > section_threshold
        ]
        
        fusion_chunks = []
        if valid_section_ids:
            # Retrieve all chunks corresponding to the valid sections.
            fusion_chunks = [
                chunk for chunk in chunks if chunk["id"] in valid_section_ids
            ]
        
        num_from_sections = len(fusion_chunks)
        remainder = top_k - num_from_sections
        
        if remainder > 0:
            print("⚠️ Some sections did not meet the threshold; retrieving additional content chunks via fallback search.")
            # Retrieve additional chunks using full content similarity for the remaining slots.
            fallback_chunks = search_index(chunk_index, query_embedding, chunks, remainder)
            fusion_chunks.extend(fallback_chunks)
        
        # print(fusion_chunks)
        return fusion_chunks[:top_k]
