"""Core RAG logic: load docs, embed with OpenAI, store/retrieve in ChromaDB."""

from __future__ import annotations

import io
from pathlib import Path
from typing import List, Optional

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_text_from_bytes(data: bytes, filename: str) -> str:
    """Return plain-text content for .txt or .pdf bytes."""
    lower = filename.lower()
    if lower.endswith(".txt"):
        return data.decode("utf-8", errors="replace")
    if lower.endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(data))
        pages: List[str] = []
        for page in reader.pages:
            try:
                pages.append(page.extract_text() or "")
            except Exception:
                pass
        return "\n".join(pages)
    raise ValueError(f"Unsupported file type: {filename}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create_vectorstore(
    files: List[tuple[bytes, str]],
    *,
    openai_model: str = "text-embedding-3-small",
    embed_dimensions: int = 512,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    persist_dir: str = "./chroma_db",
) -> Chroma:
    """
    Build (or reuse) a Chroma vectorstore from a list of (bytes, filename) tuples.

    Returns a Chroma instance you can `as_retriever()` from.
    """
    # 1️⃣ Load & split documents
    docs: List[Document] = []
    for data, filename in files:
        if not data:
            continue
        try:
            text = _load_text_from_bytes(data, filename)
        except Exception as exc:
            raise ValueError(f"Failed to read {filename}: {exc}") from exc

        if not text.strip():
            continue

        # LangChain Document with metadata
        docs.append(
            Document(
                page_content=text,
                metadata={"source": filename, "file_type": filename.rsplit(".", 1)[-1]},
            )
        )

    if not docs:
        raise ValueError("No readable content found in uploaded files.")

    # 2️⃣ Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = text_splitter.split_documents(docs)

    # 3️⃣ OpenAI embeddings with reduced dimension
    embeddings = OpenAIEmbeddings(
        model=openai_model,
        dimensions=embed_dimensions,  # e.g., 512 instead of default 1536
    )

    # 4️⃣ Chroma persistent store
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir,
    )
    # persist_directory is handled by Chroma internally; no explicit .persist() needed
    # for .from_documents, but we call it to be safe:
    vectorstore.persist()

    return vectorstore


def retrieve(
    vectorstore: Chroma,
    query: str,
    k: int = 4,
) -> List[Document]:
    """Retrieve the top-k most relevant documents for *query*."""
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    return retriever.get_relevant_documents(query)


def answer_query(
    vectorstore: Chroma,
    question: str,
    *,
    openai_chat_model: str = "gpt-4o-mini",
    k: int = 4,
) -> dict:
    """
    RAG pipeline: retrieve chunks, then ask OpenAI chat to answer using them.

    Returns dict with keys: "answer", "source_documents".
    """
    from langchain.chat_models import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage
    from langchain.prompts import ChatPromptTemplate

    # Retrieve relevant chunks
    docs = retrieve(vectorstore, question, k=k)
    if not docs:
        return {
            "answer": "No relevant documents found. Please upload some text/PDF files first.",
            "source_documents": [],
        }

    # Build context from retrieved docs
    context = "\n\n".join(doc.page_content for doc in docs)

    # Simple few-shot prompt
    system_msg = """You are a helpful assistant. Answer the user's question using ONLY the context provided below. If the answer is not in the context, say "I don't have enough information to answer." Do not hallucinate.

Context:
{context}"""

    user_msg = "{question}"

    prompt = ChatPromptTemplate.from_messages(
        [("system", system_msg), ("human", user_msg)]
    )

    chat = ChatOpenAI(model=openai_chat_model, temperature=0.0)
    chain = prompt | chat

    answer = chain.invoke({"context": context, "question": question})

    return {
        "answer": answer.content if hasattr(answer, "content") else str(answer),
        "source_documents": docs,
    }