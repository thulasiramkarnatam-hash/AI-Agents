# 6-basic-rag

A basic **RAG (Retrieval-Augmented Generation)** demo built with:

- **Streamlit** — upload text/PDF files and chat with them
- **OpenAI** — `text-embedding-3-small` embeddings (512-dim) + `gpt-4o-mini` chat
- **ChromaDB** — persistent vector store
- **LangChain** — document loading, text splitting, retrieval, prompt chaining

## Features

- Upload `.txt` and `.PDF` files (multiple at once)
- Automatic chunking (`chunk_size=1000`, `chunk_overlap=200`)
- OpenAI embeddings with reduced dimension (`512`) for speed
- Persistent ChromaDB store on disk (`./chroma_db`)
- Streaming chat interface with source citations
- Clear knowledge base button (also wipes persisted DB)

## Quick start

```bash
# 1. Set your OpenAI key
export OPENAI_API_KEY="sk-..."

# 2. Run the app
streamlit run app.py
```

Then open the URL Streamlit prints, upload a few `.txt`/`.PDF` files in the sidebar, click **Process Documents**, and start chatting.

## Project layout

```
6-basic-rag/
├── app.py              # Streamlit UI
├── src/6_basic_rag/
│   ├── __init__.py
│   └── rag.py          # Core RAG logic (load → embed → store → retrieve → answer)
├── chroma_db/          # created on first run, persisted on disk
└── pyproject.toml
```

## Config (sidebar)

- Embedding model: `text-embedding-3-small`
- Embedding dimension: `512`
- Chat model: `gpt-4o-mini`
- Chunk size / overlap: `1000` / `200`
- Top-K retrieval: `4`

## Notes

- `OPENAI_API_KEY` is read from the environment first, then from Streamlit secrets.
- ChromaDB persists to `./chroma_db` so re-running the app keeps your corpus.
- Deleting the `chroma_db` folder or pressing **Clear Knowledge Base** resets the store.