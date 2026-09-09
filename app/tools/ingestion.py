import os
import re
from typing import Any
import fitz

from ..vectorstore.faiss_store import FAISSStore

"""Ingestion flow:
PDF or text file
    ->
Extract raw text
    ->
Clean text
    ->
Split text into overlapping chunks
    ->
Attach metadata such as source and optional page number
    ->
Store chunks in the vector store
"""


def clean_text(text: str) -> str:
    cleaned = text.replace("-\n", "")
    cleaned = "\n".join(line.strip() for line in cleaned.splitlines() if line.strip())
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"Page \d+ of \d+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b\d{1,3}/\d{1,3}\b", "", cleaned)
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", cleaned)
    return cleaned.strip()


def extract_pages_from_pdf(pdf_path: str) -> list[dict[str, Any]]:
    pages: list[dict[str, Any]] = []

    if fitz is None:
        raise ModuleNotFoundError("PyMuPDF is required to ingest PDF files")

    with fitz.open(pdf_path) as document:
        for page_number, page in enumerate(document, start=1):
            text = clean_text(page.get_text())
            if not text:
                continue
            pages.append({"text": text, "page": page_number})

    return pages


def extract_text_from_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        return clean_text(file.read())


def split_text_into_chunks(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between 0 and chunk_size - 1")

    words = text.split()
    if not words:
        return []

    step = chunk_size - overlap
    chunks: list[str] = []
    for start in range(0, len(words), step):
        chunk = " ".join(words[start : start + chunk_size]).strip()
        if chunk:
            chunks.append(chunk)
    return chunks


def build_chunks_and_metadata(
    file_path: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> tuple[list[str], list[dict[str, Any]]]:
    filename = os.path.basename(file_path)
    chunks: list[str] = []
    metadata: list[dict[str, Any]] = []

    if file_path.lower().endswith(".pdf"):
        pages = extract_pages_from_pdf(file_path)
        for page_item in pages:
            page_chunks = split_text_into_chunks(
                page_item["text"],
                chunk_size=chunk_size,
                overlap=overlap,
            )
            for chunk in page_chunks:
                chunks.append(chunk)
                metadata.append({"source": filename, "page": page_item["page"]})
    else:
        text = extract_text_from_file(file_path)
        for chunk in split_text_into_chunks(text, chunk_size=chunk_size, overlap=overlap):
            chunks.append(chunk)
            metadata.append({"source": filename})

    return chunks, metadata


def store_chunks_and_vectors(
    file_path: str,
    chunk_size: int = 500,
    overlap: int = 50,
    store: FAISSStore | None = None,
) -> FAISSStore:
    vector_store = store or FAISSStore()
    chunks, metadata = build_chunks_and_metadata(
        file_path,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    if chunks:
        vector_store.add(chunks=chunks, metadata=metadata)

    return vector_store
