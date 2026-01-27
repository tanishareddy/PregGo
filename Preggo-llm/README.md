# PregGo chatbot - Pregnancy Support LLM Assistant

PregGo chatbot is a specialized RAG (Retrieval-Augmented Generation) system that provides friendly, soothing pregnancy support through an AI chatbot. It combines medical knowledge from pregnancy data with supportive tone guidance to deliver compassionate, accurate responses.

## Features

- **Pregnancy Q&A Chatbot** - Ask questions about pregnancy, exercises, stages, and more
- **Dual Vector Databases** - Separate knowledge base and style examples for targeted responses
- **RAG System** - Retrieves relevant pregnancy documents before generating responses
- **Multi-Format Data Support** - Ingests CSV, JSON, and TXT files
- **Supportive Tone** - All responses follow a calm, friendly, soothing style guide
- **REST API** - Flask-based HTTP API for easy integration

## Architecture

```
Data (CSV, JSON, TXT)
        |
        v
  [Ingest Pipeline]
        |
        v
[Vector Embeddings]
        |
        v
[ChromaDB Vector Store]
    /        \
   /          \
preggo_docs  style_examples
   |            |
   v            v
[Retrieval & Ranking]
   |            |
   +----+-------+
        |
        v
  [Prompt Assembly]
        |
        v
 [Nebius LLM API]
        |
        v
   [Response]
```

## Setup

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
pip install langchain_community langchain_text_splitters
```

### 2. Environment Configuration

Create a `.env` file with:

```env
NEBIUS_API_KEY=your_api_key_here
NEBIUS_BASE_URL=https://api.nebius.com
CHROMA_DB_DIR=./chroma_db
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

**Getting a Nebius API Key:**
1. Go to [Nebius Console](https://console.nebius.ai)
2. Navigate to API Keys section
3. Create a new API key
4. Copy and paste into `.env`

### 3. Prepare Data

Add pregnancy-related data to the `./data/` folder:
- `.csv` files (CSV format)
- `.json` files (JSON objects or arrays)
- `.txt` files (plain text)

Example data files:
- `pregnancy_exercises.csv` - Exercise data
- `pregnancy_stages_training_dataset.json` - Pregnancy stage information

### 4. Ingest Data

```powershell
python ingest.py
```

This will:
- Load all data files from `./data/`
- Split into 800-character chunks
- Create vector embeddings
- Store in ChromaDB collections (`preggo_docs`)

Expected output:
```
Ingested 46 chunks to Chroma
```

### 5. Run the App

```powershell
python app.py
```

Server will start on `http://localhost:5000`

## API Endpoints

### Chat Endpoint

**POST** `/chat`

Request:
```json
{
  "message": "What exercises are safe during pregnancy?"
}
```

Response:
```json
{
  "answer": "Walking, swimming, and prenatal yoga are excellent safe exercises during pregnancy..."
}
```

### Add Style Example

**POST** `/style/add`

Request:
```json
{
  "text": "It's okay — you're doing an amazing job. Take deep breaths, we'll go step by step.",
  "meta": {"tone": "soothing", "rating": 5}
}
```

Response:
```json
{
  "status": "ok"
}
```

## Usage Example

```powershell
# Test with curl (Windows)
$body = @{message="What should I eat during pregnancy?"} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:5000/chat" -Method POST `
  -ContentType "application/json" -Body $body
```

Or use Python:
```python
import requests

response = requests.post(
    "http://localhost:5000/chat",
    json={"message": "Safe exercises during pregnancy?"}
)
print(response.json()["answer"])
```

## Files

- `app.py` - Flask REST API server
- `ingest.py` - Data ingestion and vectorization pipeline
- `style_collect.py` - Utility for adding style examples
- `requirements.txt` - Python dependencies
- `.env` - Environment configuration (API keys, URLs)
- `data/` - Input data folder (CSV, JSON, TXT files)
- `chroma_db/` - Vector database storage

## System Prompt

The assistant follows this system prompt:

> You are PregGo, a friendly, soothing pregnancy support assistant. Use the retrieved documents and the style examples to:
> 1) Answer clearly and accurately.
> 2) Be supportive, calm, and kind.
> Do not give medical diagnoses; encourage user to seek medical help for emergencies.

## How It Works

1. **User Query** - User sends a pregnancy question to `/chat`
2. **Retrieval** - System retrieves:
   - Top 3 relevant pregnancy documents from vector DB
   - Top 3 relevant style examples for tone guidance
3. **Prompt Assembly** - Combines system prompt + retrieved docs + style examples + user query
4. **LLM Generation** - Sends to Nebius LLM API for response generation
5. **Response** - Returns supportive, accurate answer

## Troubleshooting

### "Connection error" on chat requests
- Verify Nebius API key is valid and not expired
- Check internet connection
- Ensure `NEBIUS_BASE_URL` is correct

### "No module named 'langchain_community'"
```powershell
pip install langchain_community langchain_text_splitters
```

### Vector database not loading
- Ensure `./data/` folder has at least one CSV/JSON/TXT file
- Run `python ingest.py` to populate ChromaDB
- Check `./chroma_db/` directory exists and has files

### Empty responses
- Verify data was ingested: Check for 46+ chunks message
- Add more diverse pregnancy data to improve retrieval
- Check style_examples collection has examples added

## Dependencies

- `flask` - Web framework
- `langchain` - LLM orchestration
- `langchain_nebius` - Nebius AI integration
- `langchain_community` - Community integrations (Chroma, loaders)
- `chromadb` - Vector database
- `python-dotenv` - Environment variable management

## License

This project is for educational and personal use.

## Support

For issues with:
- **Nebius API** - Check [Nebius Documentation](https://docs.nebius.ai)
- **LangChain** - Check [LangChain Docs](https://python.langchain.com)
- **ChromaDB** - Check [ChromaDB Docs](https://docs.trychroma.com)

