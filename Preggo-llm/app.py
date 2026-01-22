# app.py
import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
import traceback

# LangChain pieces
from langchain_community.vectorstores import Chroma
from langchain_nebius import NebiusEmbeddings
from langchain_nebius.chat_models import ChatNebius
from langchain_core.prompts import PromptTemplate

# Setup
NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY")
NEBIUS_BASE = os.getenv("NEBIUS_BASE_URL")
CHROMA_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_db")

embeddings = NebiusEmbeddings(api_key=NEBIUS_API_KEY)
# Load collections
vectordb_docs = Chroma(persist_directory=CHROMA_DIR, collection_name="preggo_docs", embedding_function=embeddings)
vectordb_style = Chroma(persist_directory=CHROMA_DIR, collection_name="style_examples", embedding_function=embeddings)

# Create LLM client via Nebius provider
llm = ChatNebius(api_key=NEBIUS_API_KEY, model="nebius/gpt-4o-like")

# Simple prompt template that will include retrieved docs and style exemplars
SYSTEM_PROMPT = """You are PregGo, a friendly, soothing pregnancy support assistant. Use the retrieved documents and the style examples to:
1) Answer clearly and accurately.
2) Be supportive, calm, and kind.
Do not give medical diagnoses; encourage user to seek medical help for emergencies."""

chat_prompt = PromptTemplate(
    input_variables=["system_prompt", "context_docs", "style_examples", "user_input"],
    template="""{system_prompt}

Context from docs:
{context_docs}

Style examples:
{style_examples}

User asks:
{user_input}

Now reply in a calm, friendly, helpful tone. Keep it short, 2-6 sentences max.
"""
)

# Build the Flask app
app = Flask(__name__)

# Basic chat endpoint
@app.route("/chat", methods=["POST"])
def chat():
    try:
        payload = request.json
        user_input = payload.get("message", "")
        conversation_history = payload.get("history", [])  # optional list of (user, assistant) tuples
        
        # 1) retrieve top docs
        retriever = vectordb_docs.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        docs = retriever.invoke(user_input)
        context_docs = "\n\n".join([d.page_content for d in docs]) if docs else ""
        
        # 2) retrieve style exemplars
        style_retriever = vectordb_style.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        style_docs = style_retriever.invoke(user_input)
        style_examples = "\n\n".join([d.page_content for d in style_docs]) if style_docs else ""
        
        # 3) compose prompt
        prompt_text = chat_prompt.format(
            system_prompt=SYSTEM_PROMPT,
            context_docs=context_docs,
            style_examples=style_examples,
            user_input=user_input
        )
        
        # 4) ask Nebius LLM
        try:
            llm_response = llm.invoke(prompt_text)
            # Extract text from response
            answer = llm_response.content if hasattr(llm_response, "content") else str(llm_response)
        except Exception as llm_error:
            print(f"LLM Error: {llm_error}")
            print(f"API Key present: {bool(NEBIUS_API_KEY)}")
            raise
        
        # Return
        return jsonify({"answer": answer})
    except Exception as e:
        traceback.print_exc()
        print(f"Full error details: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Endpoint to add style example (collecting data from users/admins)
@app.route("/style/add", methods=["POST"])
def add_style():
    try:
        payload = request.json
        text = payload["text"]
        meta = payload.get("meta", {"tone": "soothing", "rating": 5})
        # Simple add to chroma
        from langchain_core.documents import Document
        doc = Document(page_content=text, metadata=meta)
        vectordb_style.add_documents([doc])
        vectordb_style.persist()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host=os.getenv("FLASK_HOST","0.0.0.0"), port=int(os.getenv("FLASK_PORT",5000)))
