
from src.agents.company_info_rag_agent import CompanyInfoRAGAgent

if __name__ == "__main__":
    agent = CompanyInfoRAGAgent()
    user_question = "What is Meril's mission and vision?"

    answer = agent.run(user_question)
    print("\n[Answer]:", answer)
