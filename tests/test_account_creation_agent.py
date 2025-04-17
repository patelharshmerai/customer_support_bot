# File: scripts/test_account_creation.py

from src.agents.account_creation_agent import AccountCreationAgent

def test_account_creation():
    print("[TEST] Starting AccountCreationAgent test...")
    
    # Simulated user inputs
    phone = "9876543210"
    name = "Harsh"

    # Initial dummy state
    state = {
        "phone": phone,
        "name": name,
        "input": "",
        "chat_history": [],
        "output": {}
    }

    # Instantiate and run the agent
    agent = AccountCreationAgent()
    new_state = agent.run(phone=phone, user_name=name, state=state)

    # Print bot response
    print("\n[Bot]:", new_state["output"]["response"])

    # Optional: Log some messages to chat history
    print("\n[✓] Test complete. Check MongoDB for stored user + chat history.")

if __name__ == "__main__":
    test_account_creation()
