# File: src/agents/product_match_agent.py

import os
from dotenv import load_dotenv
from typing import List
from pinecone import Pinecone
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = "product-index"

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L12-v2")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro-exp-03-25", temperature=0.3)

class ProductMatchAgent:
    def __init__(self, k: int = 3):
        self.k = k

    def retrieve_products(self, query: str) -> List[Document]:
        print("[ProductMatchAgent] Embedding query and retrieving from Pinecone...")
        query_embedding = embedding_model.embed_query(query)
        results = index.query(vector=query_embedding, top_k=self.k, include_metadata=True)
        return [
            Document(page_content=match["metadata"].get("text", ""), metadata={"score": match["score"]})
            for match in results["matches"]
        ]

    def generate_response(self, query: str, context_chunks: List[Document]) -> str:
        context_text = "\n\n".join([doc.page_content for doc in context_chunks])
        prompt = f"""
You are a product assistant for a medical device company.

Use the following product information to help the user find a suitable product:

{context_text}

User Query: {query}

Answer like this:
"Based on the company’s official information, here’s what we know: ..."
"""
        print("[ProductMatchAgent] Generating response using Gemini...")
        response = llm.invoke(prompt)
        return response.content.strip()

    def run(self, query: str, state: dict) -> dict:
        print("[ProductMatchAgent] Running agent for query:", query)
        try:
            chunks = self.retrieve_products(query)
            msg = (
                self.generate_response(query, chunks)
                if chunks else
                "Sorry, I couldn’t find a matching product in our catalog."
            )
        except Exception as e:
            print("[ProductMatchAgent] Error:", e)
            msg = "An error occurred while retrieving product information."

        return {**state, "output": {"agent": "ProductMatchAgent", "response": msg}}
