import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage
from src.config import llm
from src.state import AgentState, MCPContext
from src.prompts import SYSTEM_PROMPT
from src.tools import retrieve_tool, mock_db_tool

# ---------- Bind tools to LLM ----------
tools = [retrieve_tool, mock_db_tool]
llm_with_tools = llm.bind_tools(tools)

# ---------- MCP Structured Output (forces context) ----------
def enforce_mcp_context(query: str) -> MCPContext:
    """Use LLM's structured output to populate MCPContext before any tool."""
    structured_llm = llm.with_structured_output(MCPContext)
    prompt = (
        f"User query: {query}\n"
        "Based on this, output an MCPContext with required_action one of: "
        "'retrieve_only', 'db_lookup', or 'both'.\n"
        "For customer_balance, if not requested or unknown, output null (not 'None' or 'none')."
    )
    return structured_llm.invoke(prompt)

# ---------- Node: Agent ----------
def agent_node(state: AgentState):
    messages = state["messages"]
    # Prepend system prompt if not present
    if not any(isinstance(m, HumanMessage) and m.content == SYSTEM_PROMPT for m in messages):
        messages = [HumanMessage(content=SYSTEM_PROMPT)] + messages
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# ---------- Node: Tools (using ToolNode) ----------
tool_node = ToolNode(tools)

def tools_node(state: AgentState):
    # ToolNode handles execution automatically, including interrupt simulation if needed.
    # For demo, we just call it.
    result = tool_node.invoke(state)
    return result  # returns dict with "messages"

# ---------- Router ----------
def router(state: AgentState) -> Literal["tools", END]:
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "tools"
    return END

# ---------- Build Graph ----------
def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", tools_node)

    builder.set_entry_point("agent")
    builder.add_conditional_edges("agent", router)
    builder.add_edge("tools", "agent")

    return builder.compile()

# Optional: pre-invoke MCP context builder (exposed for demo)
def get_mcp_context(query: str) -> MCPContext:
    return enforce_mcp_context(query)