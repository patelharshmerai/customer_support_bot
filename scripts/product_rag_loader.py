# File: scripts/product_rag_loader.py

import json
import os
from dotenv import load_dotenv
from typing import List
from langchain_community.embeddings import HuggingFaceEmbeddings
from pinecone import Pinecone

# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = "product-index"
PRODUCT_DATA_PATH = "src/data/product_data.json"

def load_products(json_path: str) -> List[str]:
    with open(json_path, "r") as file:
        products = json.load(file)

    chunks = []
    for product in products:
        product_text = f"""Product Name: {product['name']}
Category: {product['category']}
Description: {product['description']}"""
        chunks.append(product_text)
    return chunks

def build_vectorstore(chunks: List[str]):
    print("[*] Connecting to Pinecone...")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)

    print("[*] Initializing embedding model...")
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L12-v2")

    print("[*] Generating embeddings...")
    embeddings = embedding_model.embed_documents(chunks)

    print("[*] Uploading to Pinecone...")
    vectors = [
        {
            "id": f"product-{i}",
            "values": embeddings[i],
            "metadata": {"text": chunks[i], "source": "product_data"}
        }
        for i in range(len(chunks))
    ]

    index.upsert(vectors=vectors)
    print("[✓] Done. Product data uploaded.")

def run_pipeline():
    print("[*] Loading product_data.json...")
    chunks = load_products(PRODUCT_DATA_PATH)
    print(f"[*] Total products: {len(chunks)}")
    build_vectorstore(chunks)

if __name__ == "__main__":
    run_pipeline()
