# File: scripts/company_rag_loader.py

import json
import os
from typing import List
from dotenv import load_dotenv

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from pinecone import Pinecone

# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = "company-index"
COMPANY_DATA_PATH = "src/data/company_data.json"

def load_company_data(json_path: str) -> str:
    with open(json_path, "r") as file:
        data = json.load(file)
    return "\n\n".join([f"{key}: {value}" for key, value in data.items()])

def chunk_text(text: str, chunk_size_chars: int = 1600, chunk_overlap_chars: int = 200) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size_chars,
        chunk_overlap=chunk_overlap_chars,
        length_function=len
    )
    return splitter.split_text(text)

def build_vectorstore(chunks: List[str]):
    print("[*] Connecting to Pinecone...")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)

    print("[*] Initializing HuggingFace embedding model...")
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L12-v2")


    print("[*] Generating embeddings...")
    embeddings = embedding_model.embed_documents(chunks)

    print("[*] Uploading data to Pinecone...")
    vectors = [
        {
            "id": f"chunk-{i}",
            "values": embeddings[i],
            "metadata": {"text": chunks[i], "source": "company_data"}
        }
        for i in range(len(chunks))
    ]

    index.upsert(vectors=vectors)
    print("[✓] Done! Data uploaded to Pinecone.")

def run_pipeline():
    print("[*] Loading company_data.json...")
    text = load_company_data(COMPANY_DATA_PATH)

    print("[*] Splitting text into fixed-size chunks...")
    chunks = chunk_text(text)
    print(f"[*] Total chunks created: {len(chunks)}")
    build_vectorstore(chunks)

if __name__ == "__main__":
    run_pipeline()
