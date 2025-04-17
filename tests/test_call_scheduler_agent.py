
from src.agents.call_scheduler_agent import CallSchedulerAgent

def test_call_scheduler():
    agent = CallSchedulerAgent()

    name = "Harsh"
    phone = "6261578341"

    response = agent.run(name, phone,{})
    print("[Bot]:", response)

if __name__ == "__main__":
    test_call_scheduler()
