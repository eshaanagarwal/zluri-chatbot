import faiss
import numpy as np
from typing import List, Dict, Tuple
import json

def build_dual_faiss_indices(
    chunks: List[Dict],
) -> Tuple[faiss.IndexFlatIP, faiss.IndexFlatIP, List[Dict]]:
    """
    Create two FAISS indices:
    - section_index: from section embeddings
    - chunk_index: from full chunk embeddings
    Returns:
    - section_index: FAISS index for section titles
    - chunk_index: FAISS index for full content chunks
    - chunks: original chunk data with metadata
    """
    
    # Extract section and chunk embeddings
    section_embeddings = np.array(
        [chunk["section_embedding"] for chunk in chunks]
    ).astype("float32")

    chunk_embeddings = np.array([chunk["chunk_embedding"] for chunk in chunks]).astype(
        "float32"
    )

    dim = chunk_embeddings.shape[1]

    section_index = faiss.IndexFlatIP(dim)  # cosine sim (normalized embeddings)
    chunk_index = faiss.IndexFlatIP(dim)

    section_index.add(section_embeddings)
    chunk_index.add(chunk_embeddings)

    # Store the original chunks with their metadata
    # This is important for retrieval later
    for i, chunk in enumerate(chunks):
        chunk["id"] = i  # Add an ID to each chunk for reference

    # # Create a mapping from section name to chunk IDs
    # section_to_chunks = {}
    # for i, chunk in enumerate(chunks):
    #     section_name = chunk["section"]
    #     if section_name not in section_to_chunks:
    #         section_to_chunks[section_name] = []
    #     section_to_chunks[section_name].append(i)
    # Create a "clean" version of chunks without the embeddings for saving.

    
    saved_chunks = []
    for chunk in chunks:
        # Keep only keys you want to persist: for example, id, text, and section.
        clean_chunk = {
            "id": chunk["id"],
            "text": chunk["text"],
            "section": chunk["section"]
        }
        saved_chunks.append(clean_chunk)
    
    # Save clean chunk data to JSON.
    with open("indexed_chunks.json", "w", encoding="utf-8") as f:
        json.dump(saved_chunks, f, indent=4)
    print("Indexed chunks saved successfully.")


    # saved indexed to reload instead of re-embedding
    print("Saving FAISS indices to disk...")
    faiss.write_index(section_index, "section_index.index")
    faiss.write_index(chunk_index, "chunk_index.index")
    print("FAISS indices saved successfully.")

    return section_index, chunk_index, chunks


def search_index(
    index: faiss.IndexFlatIP,
    query_embedding: np.ndarray,
    chunks: List[Dict],
    top_k: int = 3,
) -> List[Dict]:
    """
    Perform a search on the given FAISS index and return top-k matching chunks.
    """
    scores, indices = index.search(query_embedding.reshape(1, -1), top_k)
    return [chunks[i] for i in indices[0]]
