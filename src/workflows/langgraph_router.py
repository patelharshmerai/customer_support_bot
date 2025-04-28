import sys
import os

# Find the project root folder dynamically
def find_project_root(root_folder_name="Customer_support"):
    current_path = os.path.abspath(os.getcwd())
    while True:
        if os.path.basename(current_path) == root_folder_name:
            return current_path
        parent_path = os.path.dirname(current_path)
        if parent_path == current_path:  # reached system root
            raise Exception(f"Project root folder '{root_folder_name}' not found.")
        current_path = parent_path

# Add the root folder to sys.path
project_root = find_project_root()
sys.path.append(project_root)


# File: src/agents/account_creation_agent.py

import os
import sys
from datetime import datetime
from typing import Annotated
from typing_extensions import TypedDict

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda, Runnable, RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults

from langgraph.graph.message import AnyMessage, add_messages
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

# ---- Tool Imports ----
from src.agents.call_scheduler_agent import call_scheduler_tool
from src.agents.account_creation_agent import account_creation_tool
from src.agents.company_info_rag_agent import company_info_rag_tool
from src.agents.product_match_agent import product_match_tool


# ---- Load Environment Variables ----
load_dotenv()

# ---- Define LangGraph State ----
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

# ---- Error Handler for Tools ----
def handle_tool_error(state) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }

# ---- Helper to Create Tool Node with Fallback ----
def create_tool_node_with_fallback(tools: list) -> dict:
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )

# ---- Prompt ----
primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful customer support assistant for Meril Life Sciences. "
            "Use the provided tools to search for company or product or to assist the user's queries. "
            "When searching, be persistent. Expand your query bounds if the first search returns no results. "
            "If a search comes up empty, expand your search before giving up. "
            "Search Google using the TavilySearchResults tool if the info is not provided in the company knowledge base."
            "dont fulfill any request that is not related to the company or product."
            "be fun loving and flirty and use emojis in your response."
            "\n\nCurrent user:\n<User>\n{user_info}\n</User>"
            "\nCurrent time: {time}.",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now)

# ---- LLM ----
llm = ChatGoogleGenerativeAI(model="models/gemini-2.0-flash-lite", temperature=0.3)

# Define a custom Runnable that logs tool calls
class TavilySearchResultsWithLogging(TavilySearchResults):
    def _run(self, state):
        print("TavilySearchResults tool is being called.")
        # Call the original functionality here
        return super()._run(state)

# ---- Tools ----
part_1_tools = [
      # Log before calling TavilySearchResults
    TavilySearchResults(max_results=1),
    account_creation_tool,
    call_scheduler_tool,
    company_info_rag_tool,
    product_match_tool,
    # TavilySearchResultsWithLogging(max_results=1)
]

# ---- Runnable Assistant Wrapper ----
class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: dict, config: RunnableConfig):
        configuration = config.get("configurable", {})
        name = configuration.get("name", "Guest")
        phone = configuration.get("Phone no", "0000000000")

        # Inject user info into state
        state = {
            **state,
            "user_info": f"{name} ({phone})"
        }

        # Retry loop to ensure response
        while True:
            result = self.runnable.invoke(state)
            if not result.tool_calls and (
                not result.content or
                (isinstance(result.content, list) and not result.content[0].get("text"))
            ):
                messages = state.get("messages", []) + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break

        return {"messages": result}

# ---- Final Runnable ----
part_1_assistant_runnable = primary_assistant_prompt | llm.bind_tools(part_1_tools)

# ---- LangGraph Build ----
builder = StateGraph(State)
builder.add_node("assistant", Assistant(part_1_assistant_runnable))
builder.add_node("tools", create_tool_node_with_fallback(part_1_tools))
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")

# ---- Memory (in-memory for now) ----
memory = MemorySaver()

# ---- Compile Final Graph ----
part_1_graph = builder.compile(checkpointer=memory)
