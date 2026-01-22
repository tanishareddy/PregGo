# ingest.py
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, CSVLoader, JSONLoader
from langchain_nebius import NebiusEmbeddings
import json

NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY")
NEBIUS_BASE = os.getenv("NEBIUS_BASE_URL")

embeddings = NebiusEmbeddings(api_key=NEBIUS_API_KEY)

# Read files in ./data
data_dir = "./data"
all_docs = []
for filename in os.listdir(data_dir):
    filepath = os.path.join(data_dir, filename)
    try:
        if filename.endswith(".txt"):
            loader = TextLoader(filepath, encoding="utf-8")
            docs = loader.load()
            all_docs.extend(docs)
        elif filename.endswith(".csv"):
            loader = CSVLoader(filepath)
            docs = loader.load()
            all_docs.extend(docs)
        elif filename.endswith(".json"):
            # Handle JSON files - support both array and object formats
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                # Array of objects
                for item in data:
                    content = json.dumps(item) if isinstance(item, dict) else str(item)
                    from langchain_core.documents import Document
                    all_docs.append(Document(page_content=content, metadata={"source": filename}))
            elif isinstance(data, dict):
                # Single object
                content = json.dumps(data)
                from langchain_core.documents import Document
                all_docs.append(Document(page_content=content, metadata={"source": filename}))
    except Exception as e:
        print(f"Error loading {filename}: {e}")

# Split into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
chunks = splitter.split_documents(all_docs)

# Create or connect to Chroma
persist_directory = os.getenv("CHROMA_DB_DIR", "./chroma_db")
vectordb = Chroma.from_documents(chunks, embeddings, collection_name="preggo_docs", persist_directory=persist_directory)
vectordb.persist()
print("Ingested", len(chunks), "chunks to Chroma")
