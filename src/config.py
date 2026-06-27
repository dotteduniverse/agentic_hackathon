import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

load_dotenv()

QDRANT_PATH = os.getenv("QDRANT_PATH", "./qdrant_db")

# ---------- Lazy Qdrant client (prevents lock issues at import time) ----------
_qdrant_client = None

def get_qdrant_client():
    global _qdrant_client
    if _qdrant_client is None:
        from qdrant_client import QdrantClient
        _qdrant_client = QdrantClient(path=QDRANT_PATH)
    return _qdrant_client

# ---------- Embeddings ----------
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
)

# ---------- Vector Store & Retriever getters ----------
def get_vector_store(collection_name: str = "regulatory_docs"):
    return QdrantVectorStore(
        client=get_qdrant_client(),
        collection_name=collection_name,
        embedding=embeddings,
    )

def get_retriever(collection_name: str = "regulatory_docs", k: int = 4):
    vs = get_vector_store(collection_name)
    return vs.as_retriever(search_kwargs={"k": k})

# ---------- LLM ----------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if GROQ_API_KEY:
    llm = ChatGroq(model="qwen/qwen3.6-27b", api_key=GROQ_API_KEY, temperature=0.1)
else:
    from langchain_community.chat_models import ChatOllama
    llm = ChatOllama(model="llama3", base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))