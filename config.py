import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

load_dotenv()

# ---------- Qdrant ----------
QDRANT_PATH = os.getenv("QDRANT_PATH", "./qdrant_db")
# If using cloud, set QDRANT_URL and QDRANT_API_KEY instead
qdrant_client = QdrantClient(path=QDRANT_PATH)

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},  # or "cuda" if GPU
)

vector_store = QdrantVectorStore(
    client=qdrant_client,
    collection_name="regulatory_docs",
    embedding=embeddings,
)
retriever = vector_store.as_retriever(search_kwargs={"k": 4})

# ---------- LLM ----------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if GROQ_API_KEY:
    llm = ChatGroq(
        model="mixtral-8x7b-32768",  # or "llama3-70b-8192"
        api_key=GROQ_API_KEY,
        temperature=0.1,
    )
else:
    # Fallback to Ollama (local)
    from langchain_community.chat_models import ChatOllama
    llm = ChatOllama(model="llama3", base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    print("⚠️  Using Ollama (local) – slower but free.")