import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import List, TypedDict, Annotated, Optional
import operator
from langchain_core.messages import BaseMessage
from pydantic import BaseModel

# ---------- MCP Context Schema (JD key requirement) ----------
class MCPContext(BaseModel):
    """Model Context Protocol – structured context passed between agent and tools."""
    user_intent: str
    retrieved_policies: List[str]
    customer_balance: Optional[str] = None
    required_action: str  # e.g., "retrieve_only", "db_lookup", "both"

# ---------- LangGraph State ----------
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    mcp_context: Optional[MCPContext]  # populated before tools