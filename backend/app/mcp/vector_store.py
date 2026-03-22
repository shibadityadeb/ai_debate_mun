
from typing import Dict, List, Optional
import uuid

import chromadb
from chromadb.config import Settings

from app.mcp.embedder import Embedder


class VectorStore:
    """Lightweight local vector store backed by ChromaDB."""

    def __init__(
        self,
        collection_name: str = "default_collection",
        persist_directory: Optional[str] = "./chromadb",
    ) -> None:
        """Initialize the ChromaDB collection and embedder.
        Args:
            collection_name: Name of the ChromaDB collection to use.
            persist_directory: Local directory to persist vectors.
        """
        self._client = chromadb.Client(
            Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=persist_directory,
            )
        )
        existing = {c.name for c in self._client.list_collections()}
        if collection_name in existing:
            self._collection = self._client.get_collection(name=collection_name)
        else:
            self._collection = self._client.create_collection(name=collection_name)

        self._embedder = Embedder()

    def add_documents(self, texts: List[str], metadatas: List[Dict]) -> List[str]:
        """Add documents, metadata and ids to the vector store.
        Args:
            texts: List of document text strings.
            metadatas: List of metadata dictionaries, e.g. source URL.

        Returns:
            A list of generated ids for the inserted documents.
        """
        if not isinstance(texts, list) or not isinstance(metadatas, list):
            raise TypeError("texts and metadatas must both be lists")

        if len(texts) != len(metadatas):
            raise ValueError("texts and metadatas must have the same length")

        ids = [str(uuid.uuid4()) for _ in texts]
        embeddings = self._embedder.embed(texts)

        self._collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )

        return ids

    def query(self, query_text: str, n_results: int = 3) -> List[Dict]:
        """Query the vector store and return the top relevant documents.
        Args:
            query_text: Query string to search for.
            n_results: Number of nearest neighbors to return.

        Returns:
            List of result dicts containing id, document, metadata, and distance.
        """
        if not isinstance(query_text, str):
            raise TypeError("query_text must be a string")

        query_embedding = self._embedder.embed([query_text])[0]

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["ids", "documents", "metadatas", "distances"],
        )

        documents = []
        for idx, doc_id in enumerate(results.get("ids", [])):
            documents.append(
                {
                    "id": doc_id,
                    "document": results.get("documents", [[]])[0][idx],
                    "metadata": results.get("metadatas", [[]])[0][idx],
                    "distance": results.get("distances", [[]])[0][idx],
                }
            )

        return documents

