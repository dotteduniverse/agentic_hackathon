from typing import List, TypedDict, Annotated, Optional, Literal
import operator
from langchain_core.messages import BaseMessage
from pydantic import BaseModel

# ---------- MCP Context (from Day 1) ----------
class MCPContext(BaseModel):
    user_intent: str
    retrieved_policies: List[str]
    customer_balance: Optional[str] = None
    required_action: str  # "retrieve_only", "db_lookup", "both", "plan_only"

# ---------- Day 1 State ----------
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    mcp_context: Optional[MCPContext]

# ---------- Sprint 2: Supervisor State ----------
class SupervisorState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    next: str  # Which agent to call next: "retriever", "db_agent", "planner", "FINISH"
    mcp_context: Optional[MCPContext]