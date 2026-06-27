"""
Interactive demo – run with: python demo.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langchain_core.messages import HumanMessage
from src.graph import build_graph, get_mcp_context
from src.state import AgentState

def main():
    graph = build_graph()
    print("🤖 Agentic AI Hackathon – Day 1")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("\n> ")
        if user_input.lower() in ["exit", "quit"]:
            break

        # Step 1: Enforce MCP context (showcase JD skill)
        mcp = get_mcp_context(user_input)
        print(f"📋 MCP Context generated: {mcp.model_dump_json(indent=2)}")

        # Step 2: Invoke graph
        state = {"messages": [HumanMessage(content=user_input)], "mcp_context": mcp}
        result = graph.invoke(state)

        final_msg = result["messages"][-1]
        print(f"\n✅ Final Answer:\n{final_msg.content}")

        # Optional: show tool calls
        for msg in result["messages"]:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                print(f"🔧 Tool calls: {[tc['name'] for tc in msg.tool_calls]}")

if __name__ == "__main__":
    main()