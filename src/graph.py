from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langchain_core.messages import AIMessage, HumanMessage
from config import llm
from src.state import AgentState, MCPContext
from src.prompts import SYSTEM_PROMPT, HUMAN_CONFIRM_PROMPT
from src.tools import retrieve_tool, mock_db_tool

# ---------- Bind tools to LLM ----------
tools = [retrieve_tool, mock_db_tool]
tool_executor = ToolExecutor(tools)
llm_with_tools = llm.bind_tools(tools)

# ---------- MCP Structured Output (forces context) ----------
def enforce_mcp_context(query: str) -> MCPContext:
    """Use LLM's structured output to populate MCPContext before any tool."""
    structured_llm = llm.with_structured_output(MCPContext)
    prompt = (
        f"User query: {query}\n"
        "Based on this, output an MCPContext with required_action one of: "
        "'retrieve_only', 'db_lookup', or 'both'."
    )
    return structured_llm.invoke(prompt)

# ---------- Node: Agent ----------
def agent_node(state: AgentState):
    messages = state["messages"]
    # Prepend system prompt if not present
    if not any(isinstance(m, type(messages[0])) and m.content == SYSTEM_PROMPT for m in messages):
        messages = [HumanMessage(content=SYSTEM_PROMPT)] + messages
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# ---------- Node: Tools ----------
def tools_node(state: AgentState):
    last_msg = state["messages"][-1]
    # Check if human confirmation is needed for DB tool
    if last_msg.tool_calls:
        for tc in last_msg.tool_calls:
            if tc["name"] == "mock_db_tool":
                # Simulate interrupt – in real prod, you'd pause and wait for input.
                # For demo, we auto-confirm but print the warning.
                print("\n🔴 [INTERRUPT] DB access requested. Confirm? (auto-confirming for demo)")
                # In production: use `graph.interrupt()` or a separate input loop.
                # See demo.py for manual confirm.
                pass
    result = tool_executor.invoke(last_msg)
    return {"messages": [result]}

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