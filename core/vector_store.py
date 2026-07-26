import os
import shutil
import pathlib

# ------------------------------------------------------------------
# File Paths & Directories Configuration
# ------------------------------------------------------------------
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.resolve()
CHROMA_DIR = os.path.join(PROJECT_ROOT, "vector_db")

COLLECTION_NAME = "meeting_transcript"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# ------------------------------------------------------------------
# Caching Hugging Face Embeddings Loading
# ------------------------------------------------------------------
def _load_embeddings(model_name: str):
    """Internal helper to import and instantiate the HuggingFaceEmbeddings class."""
    print(f"Loading HuggingFace Embeddings model: {model_name}...")
    from langchain_community.embeddings import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cpu"}
    )

# Try caching using Streamlit's cache_resource helper to prevent reloads on page reruns
try:
    import streamlit as st
    _load_embeddings = st.cache_resource(_load_embeddings)
except Exception:
    pass

def get_embeddings():
    """Getter for the cached Hugging Face Embeddings model."""
    return _load_embeddings(EMBEDDING_MODEL)

# ------------------------------------------------------------------
# Vector Store Operations
# ------------------------------------------------------------------
def build_vector_store(transcript: str):
    """
    Cleans up old database files, splits the transcript text into chunks,
    generates embeddings, and builds a new Chroma vector database.
    """
    print("Building vector store...")

    if not transcript or not transcript.strip():
        raise ValueError("Cannot build vector store because the transcript is empty.")

    # 1. Clean up old database directory to prevent contamination across runs
    if os.path.exists(CHROMA_DIR):
        try:
            shutil.rmtree(CHROMA_DIR)
        except Exception as e:
            print(f"Warning: Could not remove old vector store directory {CHROMA_DIR}: {e}")

    os.makedirs(CHROMA_DIR, exist_ok=True)

    # 2. Lazy load LangChain components
    from langchain_chroma import Chroma
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_core.documents import Document

    # 3. Split the transcript text into document chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_text(transcript)

    docs = [
        Document(page_content=chunk, metadata={'chunk_index': i})
        for i, chunk in enumerate(chunks)
    ]

    # 4. Generate embeddings and populate Chroma DB
    embeddings = get_embeddings()
    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DIR
    )

    return vector_store

def load_vector_store():
    """Loads an existing Chroma vector database from the persist directory."""
    from langchain_chroma import Chroma

    embeddings = get_embeddings()
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )

    return vector_store

def get_retriever(vector_store, k: int = 4):
    """Returns a retriever object from the vector store for RAG pipelines."""
    return vector_store.as_retriever(
        search_type='similarity',
        search_kwargs={"k": k}
    )