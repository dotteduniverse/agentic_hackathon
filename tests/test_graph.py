import pytest
from langchain_core.messages import HumanMessage
from src.graph import build_graph

@pytest.fixture
def graph():
    return build_graph()

def test_retrieve_only(graph):
    state = {"messages": [HumanMessage(content="What is GDPR Article 5?")]}
    result = graph.invoke(state)
    assert "retention" in result["messages"][-1].content.lower() or "personal" in result["messages"][-1].content.lower()

def test_db_only(graph):
    state = {"messages": [HumanMessage(content="Balance for A-123")]}
    result = graph.invoke(state)
    assert "4500" in result["messages"][-1].content

def test_both(graph):
    state = {"messages": [HumanMessage(content="GDPR and balance for B-456")]}
    result = graph.invoke(state)
    final = result["messages"][-1].content
    assert "balance" in final.lower() or "pending" in final.lower()