import os
import shutil
from langchain_core.documents import Document
from utils.env import get_chroma_collection_name, get_chroma_path
import chromadb
from langchain_core.embeddings import Embeddings
from langchain_chroma import Chroma

class ChromaVectorStore:
    def __init__(self, embedding_model: Embeddings):
        persistent_client = chromadb.PersistentClient(
            path=get_chroma_path(),
        )

        self._store = Chroma(
            client=persistent_client,
            collection_name=get_chroma_collection_name(),
            embedding_function=embedding_model
        )

    def add_documents(self, documents: list[Document]) -> None:
        self._store.add_documents(documents=documents, ids=[document.metadata["id"] for document in documents])

    def get_document_ids(self) -> list[str]:
        existing_ids: list[str] = set(self._store.get(include=[])["ids"])
        return existing_ids
    
    def get_documents_by_ids(self, ids: list[str]) -> list[Document]:
        documents: list[Document] = self._store.get(ids=ids)
        return documents

    def get_store(self) -> Chroma:
        return self._store

    @staticmethod
    def clear(path: str) -> None:
        if os.path.exists(path):
            shutil.rmtree(path)