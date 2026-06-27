from langchain_core.tools import tool
from config import retriever

@tool
def retrieve_tool(query: str) -> str:
    """
    Retrieve relevant regulatory policy excerpts from the Qdrant vector store.
    Input: a search query string.
    Returns: concatenated text of top 4 matching chunks.
    """
    docs = retriever.invoke(query)
    if not docs:
        return "No relevant policies found."
    return "\n\n".join([doc.page_content for doc in docs])