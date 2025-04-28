# # File: src/main.py

# import gradio as gr
# import os
# import sys
# import re

# # Find the project root folder dynamically
# def find_project_root(root_folder_name="Customer_support"):
#     current_path = os.path.abspath(os.getcwd())
#     while True:
#         if os.path.basename(current_path) == root_folder_name:
#             return current_path
#         parent_path = os.path.dirname(current_path)
#         if parent_path == current_path:
#             raise Exception(f"Project root folder '{root_folder_name}' not found.")
#         current_path = parent_path

# # Add the root folder to sys.path
# project_root = find_project_root()
# sys.path.append(project_root)

# from src.workflows.langgraph_router import part_1_graph

# # Session-local memory (clears on refresh)
# chat_history = []

# # Simple name and phone extractor (basic regex-based)
# def extract_phone(text):
#     match = re.search(r"\b\d{10}\b", text)
#     return match.group(0) if match else "NONE"

# def extract_name(text):
#     match = re.search(r"\bMy name is (\w+)", text, re.IGNORECASE)
#     return match.group(1) if match else "NONE"

# def chat(user_input, config):
#     try:
#         if config["configurable"]["Phone no"] == "NONE":
#             config["configurable"]["Phone no"] = extract_phone(user_input)
#         if config["configurable"]["name"] == "NONE":
#             config["configurable"]["name"] = extract_name(user_input)

#         result = part_1_graph.invoke(
#             {"messages": [{"role": "user", "content": user_input}]},
#             config=config
#         )
#         response = result["messages"][-1].content if result["messages"] else "No response."
#         chat_history.append((user_input, response))
#     except Exception as e:
#         chat_history.append((user_input, f"Error: {str(e)}"))
#     return chat_history, config

# # UI setup
# initial_config = {
#     "configurable": {"Phone no": "NONE", "name": "NONE"},
#     "thread_id": str(uuid.uuid4())
# }

# with gr.Blocks() as demo:
#     chatbot = gr.Chatbot()
#     state = gr.State(initial_config)
    
#     title = gr.Markdown("<h1 style='text-align: center;'>Meril Chatbot</h1>")
#     subtitle = gr.Markdown("<p style='text-align: center;'>Enter your name and phone no in chat for registration.</p>")
    
#     user_input = gr.Textbox(placeholder="Ask me anything...", scale=4)
    
#     user_input.submit(chat, inputs=[user_input, state], outputs=[chatbot, state])

# demo.launch(share=True)


import gradio as gr
import os
import sys
import re

# ---- Utility: Find root folder ----
def find_project_root(root_folder_name="Customer_support"):
    current_path = os.path.abspath(os.getcwd())
    while True:
        if os.path.basename(current_path) == root_folder_name:
            return current_path
        parent_path = os.path.dirname(current_path)
        if parent_path == current_path:
            raise Exception(f"Project root folder '{root_folder_name}' not found.")
        current_path = parent_path

project_root = find_project_root()
sys.path.append(project_root)

# ---- Import your graph ----
from src.workflows.langgraph_router import part_1_graph

import re
import phonenumbers
import spacy



# Load spaCy NER model
nlp = spacy.load("en_core_web_sm")

# 📞 Phone Number Extractor (Robust: Handles +91, formats, etc.)
def extract_phone(text):
    potential_numbers = phonenumbers.PhoneNumberMatcher(text, "IN")
    for match in potential_numbers:
        num_obj = match.number
        if phonenumbers.is_valid_number(num_obj):
            return phonenumbers.format_number(num_obj, phonenumbers.PhoneNumberFormat.E164)
    return None

# 🧠 Name Extractor using Rule-Based & NER
def extract_name(text):
    # First try rule-based method
    # rule_based_patterns = [
    #     r"(?:my name is|i am|i'm|this is|it'?s)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
    # ]
    # for pattern in rule_based_patterns:
    #     match = re.search(pattern, text, re.IGNORECASE)
    #     if match:
    #         return match.group(1).title()

    # Fallback to NER-based person name detection
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text.title()
    
    return None



# ---- Chat handler ----
def chat(user_input, config, history):
    if config["configurable"]["Phone no"] == "NONE" or config["configurable"]["name"] == "NONE":
        name = extract_name(user_input)
        phone = extract_phone(user_input)
        if name:
            config["configurable"]["name"] = name
        if phone:
            config["configurable"]["Phone no"] = phone
        
        if config["configurable"]["name"] != "NONE" and config["configurable"]["Phone no"] != "NONE":
            response = f"Thanks {config['configurable']['name']}! You're now registered with phone number {config['configurable']['Phone no']}."
        else:
            response = "Hello! please provide your name and 10-digit phone number for registration."
    else:
        try:
            result = part_1_graph.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config=config
            )
            response = result["messages"][-1].content if result["messages"] else "No response."
        except Exception as e:
            response = f"Error: {str(e)}"
    
    history.append((user_input, response))
    return history, config

# ---- Gradio UI ----
import uuid
with gr.Blocks() as demo:
    gr.Markdown("<h1 style='text-align: center;'>Customer Support Chatbot</h1>")
    chatbot = gr.Chatbot()
    user_input = gr.Textbox(placeholder="Ask me anything...", scale=4)
    state_config = gr.State({
        "configurable": {"Phone no": "NONE", "name": "NONE"},
        "thread_id": str(uuid.uuid4())
    })
    state_history = gr.State([])

    user_input.submit(chat, inputs=[user_input, state_config, state_history], outputs=[chatbot, state_config])

demo.launch(share=True)
