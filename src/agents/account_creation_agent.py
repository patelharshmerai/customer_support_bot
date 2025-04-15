# # File: src/agents/account_creation_agent.py
# from src.db.user_db import create_user, get_user_by_phone, update_user_chat

# class AccountCreationAgent:
#     """
#     A simple agent to handle user account creation flow.
#     In a real scenario, you'd integrate with an OTP or verification system.
#     """

#     def __init__(self):
#         pass
    
#     def run(self, phone: str, user_name: str) -> str:
#         """
#         Attempts to create a new user account using phone + user_name.
#         Returns a string response to be displayed to the user.
#         """
#         # Check if user already exists
#         existing_user = get_user_by_phone(phone)
#         if existing_user:
#             return (
#                 f"Welcome back, {existing_user['name']}! "
#                 f"Your account with phone {phone} already exists."
#             )
        
#         # Create user if not found
#         created = create_user(name=user_name, phone=phone)
#         if created:
#             return (
#                 f"Success! Your account has been created, {user_name}.\n"
#                 f"Your phone number is {phone}."
#             )
#         else:
#             return (
#                 "We encountered an issue creating your account. "
#                 "Please try again later or contact support."
#             )

#     def log_message(self, phone: str, message: str, sender: str = "user"):
#         """
#         Optional helper to log messages into the user's chat_history.
#         This can be integrated inside your conversation loop.
#         """
#         update_user_chat(phone, message, sender)

# File: src/agents/account_creation_agent.py

from src.db.user_db import create_user, get_user_by_phone, update_user_chat

class AccountCreationAgent:
    def __init__(self):
        pass

    def run(self, phone: str, user_name: str, state: dict) -> dict:
        existing_user = get_user_by_phone(phone)
        if existing_user:
            msg = f"Welcome back, {existing_user['name']}! Your account with phone {phone} already exists."
        else:
            created = create_user(name=user_name, phone=phone)
            msg = (
                f"Success! Your account has been created, {user_name}.\n"
                f"Your phone number is {phone}."
            ) if created else (
                "We encountered an issue creating your account. Please try again later or contact support."
            )
        return {**state, "output": {"agent": "AccountCreationAgent", "response": msg}}
