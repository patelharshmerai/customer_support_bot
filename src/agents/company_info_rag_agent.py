# File: src/agents/company_info_rag_agent.py

import os
from typing import List
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from pinecone import Pinecone

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = "company-index"

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L12-v2")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro-exp-03-25", temperature=0.3)

class CompanyInfoRAGAgent:
    def __init__(self, k: int = 3):
        self.k = k

    def retrieve_relevant_chunks(self, query: str) -> List[Document]:
        print("[CompanyInfoRAGAgent] Embedding query and querying Pinecone...")
        query_embedding = embedding_model.embed_query(query)
        results = index.query(vector=query_embedding, top_k=self.k, include_metadata=True)
        return [
            Document(page_content=match["metadata"].get("text", ""), metadata={"score": match["score"]})
            for match in results["matches"]
        ]

    def generate_answer(self, query: str, context_chunks: List[Document]) -> str:
        context_text = "\n\n".join([doc.page_content for doc in context_chunks])
        prompt = f"""
You are a helpful assistant answering questions about a medical company named Meril.

Answer conversationally, based only on the following official company information:

{context_text}

User Question: {query}

Respond like:
"Based on the company’s official information, here’s what we know: ..."
"""
        print("[CompanyInfoRAGAgent] Generating answer using Gemini...")
        response = llm.invoke(prompt)
        return response.content.strip()

    def run(self, query: str, state: dict) -> dict:
        print("[CompanyInfoRAGAgent] Running agent for query:", query)
        try:
            chunks = self.retrieve_relevant_chunks(query)
            if not chunks:
                msg = "Sorry, I couldn't find any relevant information in the company's knowledge base."
            else:
                msg = self.generate_answer(query, chunks)
        except Exception as e:
            print("[CompanyInfoRAGAgent] Error:", e)
            msg = "An error occurred while retrieving company information."

        return {**state, "output": {"agent": "CompanyInfoRAGAgent", "response": msg}}
