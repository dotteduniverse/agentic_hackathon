from langchain_core.tools import tool

# Hardcoded mock data – simulates a PostgreSQL banking system
MOCK_CUSTOMERS = {
    "A-123": {"balance": 4500.50, "last_txn": "2025-06-27", "pending": False},
    "B-456": {"balance": 120.00, "last_txn": "2025-06-26", "pending": True},
    "C-789": {"balance": 10200.00, "last_txn": "2025-06-25", "pending": False},
}

@tool
def mock_db_tool(customer_id: str) -> str:
    """
    Simulate a secure database call to retrieve customer account details.
    Requires prior confirmation (handled by interrupt in the graph).
    Input: customer_id (e.g., 'A-123')
    Returns: formatted balance and transaction status.
    """
    if customer_id not in MOCK_CUSTOMERS:
        return f"Customer {customer_id} not found."
    data = MOCK_CUSTOMERS[customer_id]
    return (
        f"Customer {customer_id}:\n"
        f"  Balance: ${data['balance']:.2f}\n"
        f"  Last Transaction: {data['last_txn']}\n"
        f"  Pending Tx: {data['pending']}"
    )