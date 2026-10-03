"""Streamlit RAG app: upload text/PDF, embed with OpenAI, store in ChromaDB, chat retrieval."""

import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Load .env if present (so users can just fill in .env instead of exporting)
load_dotenv()

# Ensure src/ is on path for `from 6_basic_rag import rag`
sys.path.insert(0, str(Path(__file__).parent / "src"))

from basic_rag import rag  # noqa: E402


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Basic RAG Demo",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

PERSIST_DIR = "./chroma_db"
OPENAI_EMBED_MODEL = "text-embedding-3-small"
EMBED_DIMENSIONS = 512
OPENAI_CHAT_MODEL = "gpt-4o-mini"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K = 4


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_api_key() -> str | None:
    """Read OPENAI_API_KEY from env or Streamlit secrets."""
    # 1. env var
    key = os.getenv("OPENAI_API_KEY")
    if key:
        return key
    # 2. Streamlit secrets
    try:
        return st.secrets.get("OPENAI_API_KEY")  # type: ignore[attr-defined]
    except Exception:
        return None


def _init_session_state() -> None:
    defaults = {
        "vectorstore": None,
        "messages": [],
        "files_processed": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _reset_rag() -> None:
    """Clear vectorstore and chat history."""
    st.session_state.vectorstore = None
    st.session_state.messages = []
    st.session_state.files_processed = False


# ---------------------------------------------------------------------------
# Sidebar: Upload & Settings
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("📄 Document Upload")
    st.caption("Upload .txt or .PDF files to build the knowledge base.")

    uploaded_files = st.file_uploader(
        "Choose files",
        type=["txt", "pdf"],
        accept_multiple_files=True,
        help="You can upload multiple files at once.",
    )

    if st.button("🔄 Process Documents", type="primary", disabled=not uploaded_files):
        if not _get_api_key():
            st.error("❌ OPENAI_API_KEY not set. Add it to your environment or Streamlit secrets.")
        else:
            with st.spinner("Embedding & storing documents…"):
                try:
                    file_bytes = [(f.read(), f.name) for f in uploaded_files]
                    st.session_state.vectorstore = rag.create_vectorstore(
                        files=file_bytes,
                        openai_model=OPENAI_EMBED_MODEL,
                        embed_dimensions=EMBED_DIMENSIONS,
                        chunk_size=CHUNK_SIZE,
                        chunk_overlap=CHUNK_OVERLAP,
                        persist_dir=PERSIST_DIR,
                    )
                    st.session_state.files_processed = True
                    st.success(f"✅ Indexed {len(file_bytes)} file(s) into ChromaDB.")
                except Exception as exc:
                    st.error(f"Failed to process documents: {exc}")

    st.divider()
    st.subheader("⚙️ Settings")
    st.text_input("Embedding Model", value=OPENAI_EMBED_MODEL, disabled=True)
    st.number_input("Embedding Dimension", value=EMBED_DIMENSIONS, disabled=True)
    st.text_input("Chat Model", value=OPENAI_CHAT_MODEL, disabled=True)
    st.number_input("Chunk Size", value=CHUNK_SIZE, disabled=True)
    st.number_input("Chunk Overlap", value=CHUNK_OVERLAP, disabled=True)
    st.number_input("Top-K Retrieval", value=TOP_K, disabled=True)

    st.divider()
    if st.button("🗑️ Clear Knowledge Base", type="secondary"):
        _reset_rag()
        # Also delete persisted ChromaDB on disk
        import shutil

        if Path(PERSIST_DIR).exists():
            shutil.rmtree(PERSIST_DIR, ignore_errors=True)
        st.rerun()


# ---------------------------------------------------------------------------
# Main: Chat Interface
# ---------------------------------------------------------------------------

def main() -> None:
    _init_session_state()

    st.title("🔍 Basic RAG with OpenAI + ChromaDB")
    st.caption(
        "Upload text/PDF files in the sidebar, then ask questions. "
        "Uses `text-embedding-3-small` (512-d) + `gpt-4o-mini` + persistent ChromaDB."
    )

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("📚 Sources"):
                    for i, src in enumerate(msg["sources"], 1):
                        st.markdown(f"**Source {i}** — `{src.metadata.get('source', 'unknown')}`")
                        st.code(src.page_content[:500] + ("…" if len(src.page_content) > 500 else ""))

    # Chat input
    if prompt := st.chat_input("Ask a question about your documents…"):
        if not _get_api_key():
            st.error("❌ OPENAI_API_KEY not set.")
            return

        if not st.session_state.vectorstore:
            st.warning("⚠️ No documents indexed yet. Upload & process files first.")
            return

        # User message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                try:
                    result = rag.answer_query(
                        st.session_state.vectorstore,
                        prompt,
                        openai_chat_model=OPENAI_CHAT_MODEL,
                        k=TOP_K,
                    )
                    answer = result["answer"]
                    sources = result["source_documents"]

                    st.markdown(answer)

                    if sources:
                        with st.expander("📚 Sources"):
                            for i, src in enumerate(sources, 1):
                                st.markdown(f"**Source {i}** — `{src.metadata.get('source', 'unknown')}`")
                                st.code(src.page_content[:500] + ("…" if len(src.page_content) > 500 else ""))

                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer, "sources": sources}
                    )
                except Exception as exc:
                    err_msg = f"❌ Error: {exc}"
                    st.error(err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg})


if __name__ == "__main__":
    main()