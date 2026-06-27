import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langchain_core.tools import tool
from config import get_retriever

@tool
def retrieve_tool(query: str) -> str:
    """Retrieve relevant regulatory policy excerpts from Qdrant."""
    retriever = get_retriever()  # Lazy creation
    docs = retriever.invoke(query)
    if not docs:
        return "No relevant policies found."
    return "\n\n".join([doc.page_content for doc in docs])