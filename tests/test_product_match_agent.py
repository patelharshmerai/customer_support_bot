# File: scripts/test_product_match_agent.py

from src.agents.product_match_agent import ProductMatchAgent

if __name__ == "__main__":
    agent = ProductMatchAgent()
    query = "I need a stent for treating coronary artery disease with a strong track record."

    result = agent.run(query)
    print("\n[Recommended Product]:")
    print(result)
