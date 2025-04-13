import json
from sentence_transformers import SentenceTransformer
from rag.chunker import chunk_sections
from rag.embedder import build_dual_faiss_indices
from rag.retriever import hybrid_retrieve
from config import (
    KB_PATH,
    EMBED_MODEL,
    SECTION_MATCH_THRESHOLD,
    TOP_K_RETRIEVAL,
    USE_GROQ,
)
from rag.llm import call_groq_llm
import faiss


# load knowledge_base.json 
with open(KB_PATH, 'r') as f:
    doc_sections = json.load(f)

# load embedding model
print("📡 Loading embedding model...")
model = SentenceTransformer(EMBED_MODEL)

# if indexes exist, load them
try:
    print("Loading FAISS indices from disk...")
    section_index = faiss.read_index("section_index.index")
    chunk_index = faiss.read_index("chunk_index.index")
    indexed_chunks = json.load(open("indexed_chunks.json", "r"))
    print("FAISS indices loaded successfully.")

except Exception as e:
    print(f"Error loading indices: {e}. Rebuilding indices...")
    # chunk and embed sections
    print("Create Knowledge Base Index...")
    chunks = chunk_sections(doc_sections, model)
    # build FAISS indices
    print("📦 Building FAISS indices...")
    section_index, chunk_index, indexed_chunks = build_dual_faiss_indices(chunks)
    print("FAISS indices saved successfully.")


# === INTERACTIVE QUERY LOOP ===
print("🤖 Hi! I am Zluri's chatbot. Ask me about anything related to Zluri's documentation\n")

while True:
    query = input("🔎 Ask a question (or type 'exit'): ").strip()
    if query.lower() == "exit":
        break

    top_chunks = hybrid_retrieve(
        query=query,
        model=model,
        section_index=section_index,
        chunk_index=chunk_index,
        chunks=indexed_chunks,
        section_threshold=SECTION_MATCH_THRESHOLD,
        top_k=TOP_K_RETRIEVAL,
    )

    context = "\n\n".join([chunk["text"] for chunk in top_chunks])

    # print("\n📄 Context:")
    # print(context)


    print("\n" + "="*50 + "\n")
    

    if USE_GROQ:
        answer = call_groq_llm(query, context)
        print("\n💬 Answer:", answer)
