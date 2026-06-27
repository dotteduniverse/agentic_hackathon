"""
Run this once to ingest PDFs from ./docs/ into Qdrant.
"""
import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import vector_store, embeddings, qdrant_client

def ingest_documents():
    docs_dir = Path("./docs")
    if not docs_dir.exists():
        os.makedirs(docs_dir)
        print("📂 Please place your PDFs in ./docs/ and rerun.")
        return

    all_chunks = []
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

    if not all_chunks:
        print("❌ No chunks created. Check your PDFs.")
        return

    # Delete existing collection if any
    try:
        qdrant_client.delete_collection("regulatory_docs")
    except:
        pass

    # Ingest into Qdrant
    vector_store.from_documents(
        documents=all_chunks,
        embedding=embeddings,
        collection_name="regulatory_docs",
        client=qdrant_client,
    )
    print(f"✅ Ingested {len(all_chunks)} chunks into 'regulatory_docs'.")

if __name__ == "__main__":
    ingest_documents()