
from langgraph.graph import StateGraph
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import Runnable

from src.db.user_db import get_user_by_phone, create_user
from src.db.queue_db import add_to_queue
from src.agents.account_creation_agent import AccountCreationAgent
from src.agents.call_scheduler_agent import CallSchedulerAgent
from src.agents.company_info_rag_agent import CompanyInfoRAGAgent
from src.agents.product_match_agent import ProductMatchAgent

# Define shared memory for temporary context
memory = ConversationBufferMemory(return_messages=True)

# Define the state schema
class State(dict):
    phone: str
    name: str
    input: str
    chat_history: list
    output: dict

# ---------------- NODE DEFINITIONS ----------------

def check_auth(state: State) -> dict:
    phone = state['phone']
    user = get_user_by_phone(phone)
    if user:
        return {"__condition__": "Existing"}
    return {"__condition__": "New"}


def create_account(state: State) -> State:
    agent = AccountCreationAgent()
    result = agent.run(phone=state['phone'], user_name=state['name'],state=state)
    return {**state, "output": {"agent": "AccountCreationAgent", "response": result}}

def store_user(state: State) -> State:
    create_user(name=state['name'], phone=state['phone'])
    return state

def greet_user(state: State) -> State:
    msg = f"Hi {state['name']}! How can I assist you today? You can ask about products, the company, or schedule a support call."
    return {**state, "output": {"agent": "GreetUser", "response": msg}}

def detect_intent(state: State) -> dict:
    query = state['input'].lower()
    if "company" in query or "vision" in query or "about" in query:
        return {"__condition__": "CompanyInfoRAG"}
    elif "stent" in query or "product" in query or "device" in query:
        return {"__condition__": "ProductMatchAgent"}
    elif "call" in query or "support" in query or "schedule" in query:
        return {"__condition__": "CallScheduler"}
    else:
        return {"__condition__": "CompanyInfoRAG"}  # fallback


def run_company_info_agent(state: State) -> State:
    agent = CompanyInfoRAGAgent()
    result = agent.run(state['input'],state=state)
    return {**state, "output": {"agent": "CompanyInfoRAGAgent", "response": result}}

def run_product_match_agent(state: State) -> State:
    agent = ProductMatchAgent()
    result = agent.run(state['input'],state=state)
    return {**state, "output": {"agent": "ProductMatchAgent", "response": result}}

def run_call_scheduler(state: State) -> State:
    agent = CallSchedulerAgent()
    result = agent.run(state['name'], state['phone'],state=state)
    return {**state, "output": {"agent": "CallSchedulerAgent", "response": result}}

# ---------------- GRAPH BUILD ----------------

graph = StateGraph(State)

# Add nodes
graph.add_node("CheckAuth", check_auth)
graph.add_node("AccountCreation", create_account)
graph.add_node("StoreUser", store_user)
graph.add_node("GreetUser", greet_user)
graph.add_node("IntentDetect", detect_intent)
graph.add_node("CompanyInfoRAG", run_company_info_agent)
graph.add_node("ProductMatchAgent", run_product_match_agent)
graph.add_node("CallScheduler", run_call_scheduler)

# Add edges
graph.set_entry_point("CheckAuth") # start node of the execution
graph.add_conditional_edges(
    "CheckAuth",
    {
        "New": create_account,
        "Existing": greet_user
    }
)


graph.add_edge("AccountCreation", "StoreUser")
graph.add_edge("StoreUser", "GreetUser")
graph.add_edge("GreetUser", "IntentDetect")

graph.add_conditional_edges(
    "IntentDetect",
    {
        "CompanyInfoRAG": run_company_info_agent,
        "ProductMatchAgent": run_product_match_agent,
        "CallScheduler": run_call_scheduler
    }
)



# Loop back from terminal nodes to IntentDetect
graph.add_edge("CompanyInfoRAG", "IntentDetect")
graph.add_edge("ProductMatchAgent", "IntentDetect")
graph.add_edge("CallScheduler", "IntentDetect")

# Compile the graph
workflow = graph.compile()

# Export for usage in main app
__all__ = ["workflow"]
