from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
from config import llm
from src.tools import retrieve_tool, mock_db_tool
from src.prompts import SYSTEM_PROMPT

# ---------- Retriever Agent (RAG Expert) ----------
retriever_agent = create_react_agent(
    model=llm,
    tools=[retrieve_tool],
    name="retriever_agent",
    prompt=(
        "You are a Regulatory Policy Expert. Your ONLY job is to retrieve relevant "
        "policy documents using the retrieve_tool. Answer based ONLY on retrieved content. "
        "Do NOT use any other tools. If the user asks for customer data, say you cannot help."
    ),
)

# ---------- DB Agent (Banking Data Expert) ----------
db_agent = create_react_agent(
    model=llm,
    tools=[mock_db_tool],
    name="db_agent",
    prompt=(
        "You are a Banking Data Expert. Your ONLY job is to query customer account data "
        "using the mock_db_tool. Answer with balances and transaction status. "
        "Do NOT use any other tools. If the user asks for policies, say you cannot help."
    ),
)

# ---------- Planner Agent (Reasoning Expert) ----------
planner_agent = create_react_agent(
    model=llm,
    tools=[],  # No tools - pure reasoning
    name="planner_agent",
    prompt=(
        "You are a Planning Expert. Your job is to break down complex multi-part queries "
        "into a step-by-step plan. Output a clear plan numbered 1, 2, 3... "
        "Do NOT answer the query directly - only produce the plan."
    ),
)