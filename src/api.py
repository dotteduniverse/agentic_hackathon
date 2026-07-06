import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from src.supervisor_graph import build_supervisor_graph, get_mcp_context

app = FastAPI(title="Agentic AI Hackathon", version="2.0")

# Load graph once on startup
graph = build_supervisor_graph()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    mcp_context: dict
    routing_path: str

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    try:
        # Generate MCP context
        mcp = get_mcp_context(request.query)
        # Invoke graph
        state = {"messages": [HumanMessage(content=request.query)], "next": "", "mcp_context": mcp}
        result = graph.invoke(state)
        final_msg = result["messages"][-1]
        return QueryResponse(
            answer=final_msg.content,
            mcp_context=mcp.model_dump(),
            routing_path=result.get("next", "unknown")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}