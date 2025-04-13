from typing import List, Tuple, Dict
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


def chunk_sections(
    sections, model: SentenceTransformer
) -> List[Dict]:
    """
    For each section, treat the entire section as one chunk.
    Embed both the chunk text and the heading.
    """
    chunks = []

    for section_item in tqdm(sections, desc="Chunking sections"):
        # Unpack the section item
        section_name = section_item['title']
        section_text = section_item['text']
        if not section_text.strip():
            continue

        chunk_embedding = model.encode([section_text], normalize_embeddings=True)[0]
        section_embedding = model.encode([section_name], normalize_embeddings=True)[0]

        chunks.append(
            {
                "text": section_text,
                "section": section_name,
                "chunk_embedding": chunk_embedding,
                "section_embedding": section_embedding,
            }
        )

    return chunks
