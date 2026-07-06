"""
Multi-Agent Supervisor Demo
Run with: python demo_supervisor.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.messages import HumanMessage
from src.supervisor_graph import build_supervisor_graph, get_mcp_context
from src.state import SupervisorState

def main():
    graph = build_supervisor_graph()
    print("🤖 Multi-Agent Supervisor – Sprint 2")
    print("Agents: Retriever (RAG) | DB Agent | Planner")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("\n> ")
        if user_input.lower() in ["exit", "quit"]:
            break

        # Step 1: Generate MCP context (reuse Day 1 logic)
        mcp = get_mcp_context(user_input)
        print(f"📋 MCP Context: {mcp.model_dump_json(indent=2)}")

        # Step 2: Invoke supervisor graph
        state = {
            "messages": [HumanMessage(content=user_input)],
            "next": "",
            "mcp_context": mcp,
        }
        
        result = graph.invoke(state)
        
        # Step 3: Extract and print final answer
        final_msg = result["messages"][-1]
        print(f"\n✅ Final Answer:\n{final_msg.content}")

        # Show which agents were used
        print(f"🔧 Routing path: {result.get('next', 'unknown')}")

if __name__ == "__main__":
    main()