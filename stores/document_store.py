from langchain_core.documents import Document
from stores.sqlite_store import SqliteStore
from utils.env import get_document_store_path, get_document_store_table_name

class DocumentStore:
    def __init__(self):
        self._store = SqliteStore(get_document_store_path(), get_document_store_table_name())

    def add_documents(self, documents: list[Document]) -> None:
        self._store.mset(list(zip([doc.metadata["id"] for doc in documents], documents)))

    def mget(self, keys: list[str]) -> list[Document]:
        return self._store.mget(keys)
    
    def get_store(self):
        return self._store