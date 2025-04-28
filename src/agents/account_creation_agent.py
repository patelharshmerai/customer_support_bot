# File: src/agents/account_creation_agent.py

from src.db.user_db import create_user, get_user_by_phone, update_user_chat
from langchain.tools import tool

# class AccountCreationAgent:
#     def __init__(self):
#         pass

#     def run(self, phone: str, user_name: str, state: dict) -> dict:
#         print("[AccountCreationAgent] Running account creation for:", phone)
#         try:
#             existing_user = get_user_by_phone(phone)
#             if existing_user:
#                 msg = f"Welcome back, {existing_user['name']}! Your account with phone {phone} already exists."
#             else:
#                 created = create_user(name=user_name, phone=phone)
#                 msg = (
#                     f"Success! Your account has been created, {user_name}.\nYour phone number is {phone}."
#                     if created else
#                     "We encountered an issue creating your account. Please try again later or contact support."
#                 )
#         except Exception as e:
#             print("[AccountCreationAgent] Error:", e)
#             msg = "An internal error occurred while creating your account."

#         return {**state, "output": {"agent": "AccountCreationAgent", "response": msg}}

from langchain_core.tools import tool

@tool
def account_creation_tool(phone: str, user_name: str) -> str:
    """
    Create a new user account if it doesn't exist. 
    Returns a welcome or error message.
    
    Args:
        phone (str): Phone number of the user.
        user_name (str): Name of the user.
    """
    print("[AccountCreationTool] Running account creation for:", phone)
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
        print("[AccountCreationTool] Error:", e)
        msg = "An internal error occurred while creating your account."

    return msg