# scripts/test_account_creation.py

import sys
import os
# sys.path.append(os.path.abspath("/home/harsh/Desktop/Personal_project/Customer_support/src/agent/acc"))

from src.agents.account_creation_agent import AccountCreationAgent

def test_account_creation():
    agent = AccountCreationAgent()

    # Simulated user inputs
    phone = "9876543210"
    name = "Harsh"

    # Run the agent
    response = agent.run(phone, name)
    print("[Bot]:", response)

    # Log a sample message to chat history
    agent.log_message(phone, "Hey, I need help with orthopedic implants.")
    agent.log_message(phone, "Sure! Can you describe your symptoms?", sender="bot")

    print("[✓] Test complete. Check DB for stored user.")

if __name__ == "__main__":
    test_account_creation()
