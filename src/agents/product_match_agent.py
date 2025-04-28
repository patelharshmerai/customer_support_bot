# File: src/agents/product_match_agent.py

import os
from dotenv import load_dotenv
from typing import List
from pinecone import Pinecone
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool


load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = "product-index"

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L12-v2")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro-exp-03-25", temperature=0.3)


@tool
def product_match_tool(query: str) -> str:
    """
    Find the best matching meril's product for the user's query.

    Args:
        query (str): The user's query about products.

    Returns:
        str: The generated response based on product information.
    """
    print("[ProductMatchTool] Running for query:", query)
    try:
        print("[ProductMatchTool] Embedding query and querying Pinecone...")
        query_embedding = embedding_model.embed_query(query)
        results = index.query(vector=query_embedding, top_k=3, include_metadata=True)

        if not results["matches"]:
            return "Sorry, I couldn’t find a matching product in our catalog."

        context_text = "\n\n".join(
            match["metadata"].get("text", "") for match in results["matches"]
        )

        prompt = f"""
You are a product assistant for a medical device company.

Use the following product information to help the user find a suitable product:

{context_text}

User Query: {query}

Answer like this:
"Based on the company’s official information, here’s what we know: ..."
"""
        print("[ProductMatchTool] Generating response using Gemini...")
        response = llm.invoke(prompt)
        return response.content.strip()

    except Exception as e:
        print("[ProductMatchTool] Error:", e)
        return "An error occurred while retrieving product information."
