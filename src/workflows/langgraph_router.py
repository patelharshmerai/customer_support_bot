from langgraph.graph import StateGraph
from langchain.memory import ConversationBufferMemory

from src.agents.call_scheduler_agent import CallSchedulerAgent
from src.agents.company_info_rag_agent import CompanyInfoRAGAgent
from src.agents.product_match_agent import ProductMatchAgent

# Optional: You can remove this if not using memory right now
memory = ConversationBufferMemory(return_messages=True)

# State schema
class State(dict):
    name: str
    phone: str
    input: str
    output: dict

# ---------------- NODE FUNCTIONS ----------------

def greet_user(state: State) -> State:
    print("[LangGraph] → greet_user triggered")
    msg = (
        f"Hi {state['name']}! How can I assist you today?\n"
        f"You can ask about products, the company, or schedule a support call."
    )
    return {**state, "output": {"agent": "GreetUser", "response": msg}}

def detect_intent(state: State) -> dict:
    print("[LangGraph] → detect_intent triggered")
    query = state["input"].lower()
    if any(word in query for word in ["company", "vision", "about"]):
        return {"__condition__": "CompanyInfoRAG"}
    if any(word in query for word in ["stent", "product", "device"]):
        return {"__condition__": "ProductMatchAgent"}
    if any(word in query for word in ["call", "support", "schedule"]):
        return {"__condition__": "CallScheduler"}
    return {"__condition__": "CompanyInfoRAG"}

def run_company_info_agent(state: State) -> State:
    print("[LangGraph] → run_company_info_agent triggered")
    agent = CompanyInfoRAGAgent()
    result = agent.run(state["input"], state=state)
    return {**state, "output": {"agent": "CompanyInfoRAGAgent", "response": result}}

def run_product_match_agent(state: State) -> State:
    print("[LangGraph] → run_product_match_agent triggered")
    agent = ProductMatchAgent()
    result = agent.run(state["input"], state=state)
    return {**state, "output": {"agent": "ProductMatchAgent", "response": result}}

def run_call_scheduler(state: State) -> State:
    print("[LangGraph] → run_call_scheduler triggered")
    agent = CallSchedulerAgent()
    result = agent.run(state["name"], state["phone"], state=state)
    return {**state, "output": {"agent": "CallSchedulerAgent", "response": result}}

# ---------------- GRAPH DEFINITION ----------------

graph = StateGraph(State)

graph.add_node("GreetUser", greet_user)
graph.add_node("IntentDetect", detect_intent)
graph.add_node("CompanyInfoRAG", run_company_info_agent)
graph.add_node("ProductMatchAgent", run_product_match_agent)
graph.add_node("CallScheduler", run_call_scheduler)

graph.set_entry_point("GreetUser")
graph.add_edge("GreetUser", "IntentDetect")

graph.add_conditional_edges("IntentDetect", {
    "CompanyInfoRAG": run_company_info_agent,
    "ProductMatchAgent": run_product_match_agent,
    "CallScheduler": run_call_scheduler
})

graph.add_edge("CompanyInfoRAG", "IntentDetect")
graph.add_edge("ProductMatchAgent", "IntentDetect")
graph.add_edge("CallScheduler", "IntentDetect")

# Compile workflow
workflow = graph.compile()

# Export for CLI or API
__all__ = ["workflow"]
