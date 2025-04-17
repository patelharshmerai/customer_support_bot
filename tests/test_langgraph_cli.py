# File: scripts/chat_cli.py

from src.workflows.langgraph_router import workflow
from src.db.user_db import update_user_chat
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(return_messages=True)

def run_chat():
    print("🧠 Meril Support Bot - powered by LangGraph")
    print("Type 'exit' to quit.\n")

    # Get user identity
    phone = input("📱 Enter your phone number: ")
    name = input("👤 Enter your name: ")
    
    state = {
        "phone": phone,
        "name": name,
        "input": "",
        "chat_history": [],
        "output": {}
    }

    while True:
        user_input = input("\n💬 You: ")
        if user_input.lower() in {"exit", "quit"}:
            print("👋 Goodbye!")
            break

        # Update state with new input
        state["input"] = user_input
        memory.chat_memory.add_user_message(user_input)

        # Run LangGraph
        try:
            run_name = f"{name}_{phone}_session"
            state = workflow.invoke(state, config={"run_name": run_name})

        except Exception as e:
            import traceback
            print("🚨 LangGraph Error:", e)
            traceback.print_exc()
            continue  # go back to next user input

        print("🛠️ Full state after LangGraph execution:")
        import pprint; pprint.pprint(state)
        # Get response
        output = state.get("output", {})
        response = output.get("response", "Sorry, something went wrong.")
        print(f"\n🤖 {output.get('agent', 'Bot')}: {response}")

        # Log to memory
        memory.chat_memory.add_ai_message(response)

        # Optionally push to MongoDB
        update_user_chat(phone, user_input, sender="user")
        update_user_chat(phone, response, sender="bot")

if __name__ == "__main__":
    run_chat()
