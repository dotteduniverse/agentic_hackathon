import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from config import llm
from src.state import SupervisorState, MCPContext
from src.agents import retriever_agent, db_agent, planner_agent

# ---------- Supervisor Node ----------
def supervisor_node(state: SupervisorState):
    """Supervisor analyzes query and decides which agent to call next."""
    
    # Build the prompt for the supervisor
    system_prompt = """You are a Supervisor coordinating three specialized agents:

1. **retriever_agent** - Policy/Regulatory expert (RAG). Use for: GDPR, BCBS, compliance, retention policies.
2. **db_agent** - Banking data expert. Use for: customer balances, transactions, account status.
3. **planner_agent** - Planning expert. Use for: complex multi-step queries that need breakdown.

Analyze the user's query and choose the MOST appropriate agent.
If the query has multiple parts, use planner_agent first.

Respond with ONLY the agent name: "retriever_agent", "db_agent", "planner_agent", or "FINISH".
"""
    
    messages = [HumanMessage(content=system_prompt)] + state["messages"]
    response = llm.invoke(messages)
    
    # Parse the response to get the next agent
    next_agent = response.content.strip().lower()
    
    # Map to valid agent names
    valid_agents = ["retriever_agent", "db_agent", "planner_agent", "finish"]
    if next_agent not in valid_agents:
        # Fallback: use LLM to decide via structured output
        next_agent = "finish"
    
    return {"next": next_agent}

# ---------- Worker Nodes ----------
def retriever_node(state: SupervisorState):
    """Call the retriever agent."""
    result = retriever_agent.invoke({"messages": state["messages"]})
    return {"messages": result["messages"]}

def db_node(state: SupervisorState):
    """Call the DB agent."""
    result = db_agent.invoke({"messages": state["messages"]})
    return {"messages": result["messages"]}

def planner_node(state: SupervisorState):
    """Call the planner agent."""
    result = planner_agent.invoke({"messages": state["messages"]})
    return {"messages": result["messages"]}

# ---------- Router ----------
def router(state: SupervisorState) -> Literal["retriever", "db_agent", "planner", END]:
    """Route to the next agent based on supervisor decision."""
    next_agent = state.get("next", "finish")
    
    if next_agent == "retriever_agent":
        return "retriever"
    elif next_agent == "db_agent":
        return "db_agent"
    elif next_agent == "planner_agent":
        return "planner"
    else:
        return END

# ---------- Build Graph ----------
def build_supervisor_graph():
    """Build the multi-agent supervisor graph."""
    
    builder = StateGraph(SupervisorState)
    
    # Add nodes
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("retriever", retriever_node)
    builder.add_node("db_agent", db_node)
    builder.add_node("planner", planner_node)
    
    # Set entry point
    builder.set_entry_point("supervisor")
    
    # Add conditional edges from supervisor
    builder.add_conditional_edges("supervisor", router)
    
    # All workers return to supervisor after completion
    builder.add_edge("retriever", "supervisor")
    builder.add_edge("db_agent", "supervisor")
    builder.add_edge("planner", "supervisor")
    
    return builder.compile()

# ---------- MCP Context (reused from Day 1) ----------
def get_mcp_context(query: str) -> MCPContext:
    """Generate MCP context with proper null handling."""
    structured_llm = llm.with_structured_output(MCPContext)
    prompt = (
        f"User query: {query}\n"
        "Based on this, output an MCPContext with required_action one of: "
        "'retrieve_only', 'db_lookup', 'both', or 'plan_only'.\n"
        "For customer_balance, if not requested or unknown, output null (not 'None' or 'none')."
    )
    return structured_llm.invoke(prompt)