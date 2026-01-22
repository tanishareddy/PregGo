# style_collect.py
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_nebius import NebiusEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY")
NEBIUS_BASE = os.getenv("NEBIUS_BASE_URL")
embeddings = NebiusEmbeddings(api_key=NEBIUS_API_KEY)

def add_style_example(text, tone="soothing", rating=5):
    doc = Document(page_content=text, metadata={"tone": tone, "rating": rating})
    persist_directory = os.getenv("CHROMA_DB_DIR", "./chroma_db")
    chroma = Chroma(client_settings={"persist_directory": persist_directory})
    # create collection or load
    chroma.add_documents([doc], collection_name="style_examples", embedding=embeddings)
    chroma.persist()
    print("added style example")

if __name__ == "__main__":
    sample = "It’s okay — you’re doing an amazing job. Take deep breaths, we’ll go step by step."
    add_style_example(sample)
