import asyncio
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall
from datasets import Dataset
from langchain_core.messages import HumanMessage
from src.supervisor_graph import build_supervisor_graph, get_mcp_context

# Load graph
graph = build_supervisor_graph()

# Prepare test data (golden set)
questions = [
    "What does GDPR Article 5 say about data retention?",
    "What is the balance of customer A-123?",
    "Does customer B-456 have pending transactions?",
]

ground_truths = [
    "Personal data must be kept for no longer than necessary.",
    "Balance is $4500.50.",
    "Yes, pending transactions exist.",
]

# Generate answers and contexts
answers = []
contexts = []
for q in questions:
    state = {"messages": [HumanMessage(content=q)], "next": "", "mcp_context": get_mcp_context(q)}
    result = graph.invoke(state)
    answers.append(result["messages"][-1].content)
    # Extract contexts from the last message (simplified)
    # In real scenario, you'd capture retrieved chunks; here we use dummy.
    contexts.append(["GDPR Article 5: retention limited to necessity"])

# Build dataset
data = {
    "question": questions,
    "answer": answers,
    "contexts": contexts,
    "ground_truth": ground_truths,
}
dataset = Dataset.from_dict(data)

# Evaluate
result = evaluate(dataset, metrics=[faithfulness, answer_relevancy, context_recall])
print("RAGAS Evaluation Results:")
print(result)