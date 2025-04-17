# File: src/agents/account_creation_agent.py

from src.db.user_db import create_user, get_user_by_phone, update_user_chat

class AccountCreationAgent:
    def __init__(self):
        pass

    def run(self, phone: str, user_name: str, state: dict) -> dict:
        print("[AccountCreationAgent] Running account creation for:", phone)
        try:
            existing_user = get_user_by_phone(phone)
            if existing_user:
                msg = f"Welcome back, {existing_user['name']}! Your account with phone {phone} already exists."
            else:
                created = create_user(name=user_name, phone=phone)
                msg = (
                    f"Success! Your account has been created, {user_name}.\nYour phone number is {phone}."
                    if created else
                    "We encountered an issue creating your account. Please try again later or contact support."
                )
        except Exception as e:
            print("[AccountCreationAgent] Error:", e)
            msg = "An internal error occurred while creating your account."

        return {**state, "output": {"agent": "AccountCreationAgent", "response": msg}}
