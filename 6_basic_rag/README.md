# 6-basic-rag

A basic **RAG (Retrieval-Augmented Generation)** demo built with:

- **Streamlit** — upload text/PDF files and chat with them
- **OpenAI** — `text-embedding-3-small` embeddings (512-dim) + `gpt-4o-mini` chat
- **ChromaDB** — persistent vector store
- **LangChain** — document loading, text splitting, retrieval, prompt chaining

---

## 🚀 Quick Start

### Prerequisites
- Python **3.12+**
- An **OpenAI API key** — get one at [platform.openai.com](https://platform.openai.com/api-keys)

---

### Option A: Using `uv` (recommended, fast)

```bash
# 1. Clone / navigate to the project
cd 6_basic_rag

# 2. Create & activate virtual environment (uv handles this)
uv venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies (uv syncs from pyproject.toml + uv.lock)
uv sync

# 4. Add your OpenAI key to .env
cp .env.example .env        # or just edit .env directly
# Edit .env and set: OPENAI_API_KEY=sk-...

# 5. Run the app
streamlit run app.py
```

---

### Option B: Using standard `pip` + `venv`

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Upgrade pip & install deps
pip install --upgrade pip
pip install -r requirements.txt

# 3. Add your OpenAI key
cp .env.example .env
# Edit .env → OPENAI_API_KEY=sk-...

# 4. Run
streamlit run app.py
```

---

### Option C: If `requirements.txt` doesn't exist, install manually

```bash
pip install streamlit langchain langchain-openai langchain-chroma chromadb pypdf python-dotenv openai tiktoken
```

---

## 📂 Project Layout

```
6_basic_rag/
├── app.py                 # Streamlit UI (entry point)
├── src/
│   └── basic_rag/         # Core RAG package
│       ├── __init__.py
│       └── rag.py         # load → embed → store → retrieve → answer
├── sample_docs/           # Example .txt files to try
│   └── introduction_to_rag.txt
├── chroma_db/             # Created on first run (persisted vector store)
├── .env                   # Your OpenAI key (create from .env.example)
├── .env.example           # Template for .env
├── pyproject.toml         # Project metadata + dependencies
├── uv.lock                # Locked dependency versions (uv)
└── README.md              # This file
```

---

## 🔧 Configuration (via sidebar or code)

| Setting | Default |
|---------|---------|
| Embedding model | `text-embedding-3-small` |
| Embedding dimension | `512` (reduced from 1536 for speed) |
| Chat model | `gpt-4o-mini` |
| Chunk size / overlap | `1000` / `200` |
| Top-K retrieval | `4` |

All can be adjusted in `app.py` constants at the top.

---

## 📖 Usage

1. **Run the app** → `streamlit run app.py`
2. **Open the URL** Streamlit prints (usually `http://localhost:8501`)
3. **Upload files** in the sidebar (`.txt` or `.pdf`, multiple OK)
4. Click **Process Documents** — embeds & stores in ChromaDB
5. **Chat** — ask questions; answers cite source chunks

---

## 🔑 API Key Handling

The app loads `OPENAI_API_KEY` in this order:

1. **Environment variable** (`export OPENAI_API_KEY=...` or set in shell)
2. **`.env` file** in project root (auto-loaded via `python-dotenv`)
3. **Streamlit secrets** (`.streamlit/secrets.toml` — for deployed apps)

> **Tip:** Just edit `.env` and restart the app — no need to export in terminal.

---

## 🧹 Resetting the Knowledge Base

- **In-app:** Click **Clear Knowledge Base** in sidebar (wipes DB + chat history)
- **Manual:** Delete the `chroma_db/` folder and restart

---

## 🧪 Try It Out

A sample file is included:

```bash
streamlit run app.py
# Upload: sample_docs/introduction_to_rag.txt
# Ask: "What is RAG?" or "Why does chunking matter?"
```

---

## 📦 Dependencies (from `pyproject.toml`)

| Package | Purpose |
|---------|---------|
| `streamlit` | Web UI |
| `langchain` | Core RAG orchestration |
| `langchain-openai` | OpenAI embeddings + chat |
| `langchain-chroma` | ChromaDB integration |
| `chromadb` | Vector database |
| `pypdf` | PDF text extraction |
| `python-dotenv` | `.env` file loading |
| `openai` | Direct OpenAI SDK |
| `tiktoken` | Token counting (used internally) |

---

## ⚠️ Notes

- **Python 3.12+** required (see `pyproject.toml`)
- ChromaDB persists to disk at `./chroma_db/` — survives restarts
- Embedding dimension is set to `512` (not the default 1536) for lower memory/faster search; change in `app.py` if needed
- The app uses `gpt-4o-mini` for chat — swap to `gpt-4o`, `gpt-3.5-turbo`, etc. in `app.py`
- If you see `ModuleNotFoundError: No module named 'basic_rag'`, ensure you run from the project root (`streamlit run app.py` works because it inserts `src/` into `sys.path`)