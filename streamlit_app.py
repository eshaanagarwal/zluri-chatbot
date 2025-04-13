import streamlit as st
import tempfile
from sentence_transformers import SentenceTransformer
from rag.chunker import chunk_sections
from rag.embedder import build_dual_faiss_indices
from rag.retriever import hybrid_retrieve
from rag.llm import call_groq_llm
import json
import faiss
from config import (
    EMBED_MODEL,
    SECTION_MATCH_THRESHOLD,
    TOP_K_RETRIEVAL,
    KB_PATH
)


# === Cache model ===
@st.cache_resource
def load_model():
    return SentenceTransformer(EMBED_MODEL)


# === Cache chunking + indexing ===
@st.cache_resource
def build_indices(sections, _model):
    chunks = chunk_sections(sections, _model)
    return build_dual_faiss_indices(chunks)


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


# === Main App ===
st.title("📚 Zluri Help Centre")
query = st.text_input(
    "🔎 Hi! I am Yluri's Chatbot. How can I assist you today", placeholder="e.g., How does Zluri prioritize and process application user status sources?"
)

if query:
    # 🔍 Hybrid RAG Retrieval
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

    # 🔎 Show retrieved context
    with st.expander("📄 Retrieved Context", expanded=False):
        for chunk in top_chunks:
            st.markdown(f"**🧩 Section: `{chunk['section']}`**")
            st.write(chunk["text"][:1000] + "...")
            st.divider()

    # 🤖 LLM Answer
    st.markdown("### 💬 Answer")
    with st.spinner("Generating answer using Groq..."):
        answer = call_groq_llm(query, context)
        st.success(answer)

else:
    st.info("⬆️ Ask a question to get started.")
