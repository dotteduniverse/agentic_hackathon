"""
Run this once to ingest PDFs from ./docs/ into Qdrant.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from qdrant_client.models import VectorParams, Distance
from config import get_qdrant_client, embeddings

def get_embedding_size():
    """Get the dimension of the embedding model (384 for all-MiniLM-L6-v2)."""
    return len(embeddings.embed_query("test"))

def ingest_documents():
    """Main ingestion function – creates collection and ingests all documents."""
    # Get the shared Qdrant client (lazy-loaded)
    client = get_qdrant_client()
    
    try:
        docs_dir = Path("./docs")
        if not docs_dir.exists():
            os.makedirs(docs_dir)
            print("📂 Please place your PDFs and/or .txt files in ./docs/ and rerun.")
            return

        all_chunks = []

        # ---------- Process PDFs ----------
        for pdf_path in docs_dir.glob("*.pdf"):
            print(f"📄 Processing {pdf_path.name}...")
            loader = PyPDFLoader(str(pdf_path))
            pages = loader.load()
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                separators=["\n\n", "\n", ".", " "],
            )
            chunks = splitter.split_documents(pages)
            all_chunks.extend(chunks)

        # ---------- Process .txt files ----------
        for txt_path in docs_dir.glob("*.txt"):
            print(f"📄 Processing {txt_path.name}...")
            with open(txt_path, "r", encoding="utf-8") as f:
                text = f.read()
            doc = Document(page_content=text, metadata={"source": txt_path.name})
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            chunks = splitter.split_documents([doc])
            all_chunks.extend(chunks)

        if not all_chunks:
            print("❌ No chunks created. Check your PDFs/txt files.")
            return

        # ---------- Delete existing collection (start fresh) ----------
        try:
            client.delete_collection("regulatory_docs")
            print("🗑️  Removed existing collection.")
        except Exception:
            pass  # Collection doesn't exist – fine

        # ---------- Create collection manually ----------
        vector_size = get_embedding_size()
        client.create_collection(
            collection_name="regulatory_docs",
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        print(f"✅ Created collection 'regulatory_docs' with vector size {vector_size}.")

        # ---------- Instantiate vector store and add documents ----------
        vector_store = QdrantVectorStore(
            client=client,
            collection_name="regulatory_docs",
            embedding=embeddings,
        )
        vector_store.add_documents(all_chunks)
        print(f"✅ Ingested {len(all_chunks)} chunks into 'regulatory_docs'.")

    except Exception as e:
        print(f"❌ Error during ingestion: {e}")
        raise
    finally:
        # ---------- CRITICAL: Release the file lock ----------
        client.close()
        print("✅ Qdrant client closed. Lock released.")

if __name__ == "__main__":
    ingest_documents()