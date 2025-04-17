# File: src/agents/call_scheduler_agent.py

from src.db.queue_db import add_to_queue

class CallSchedulerAgent:
    def __init__(self):
        pass

    def run(self, name: str, phone: str, state: dict) -> dict:
        print("[CallSchedulerAgent] Attempting to schedule a call for:", phone)
        try:
            scheduled = add_to_queue(name, phone)
            msg = (
                f"Thanks {name}, we've received your request. Our team will call you soon on your phone no. {phone}."
                if scheduled else
                f"Hi {name}, you’re already in the call queue. We’ll reach out as soon as possible."
            )
        except Exception as e:
            print("[CallSchedulerAgent] Error:", e)
            msg = "We encountered an error while scheduling your call. Please try again later."

        return {**state, "output": {"agent": "CallSchedulerAgent", "response": msg}}
