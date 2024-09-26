from typing import Optional
from stores.sqlite_store import SqliteStore
from utils.env import get_document_hashes_table_name, get_document_store_path

class DocumentHashesStore:
    def __init__(self):
        self._store = SqliteStore(get_document_store_path(), get_document_hashes_table_name())

    def get_document_hash(self, file_path: str) -> Optional[str]:
        file_hashes = self._store.mget([file_path])
        if file_hashes:
            return file_hashes[0]

        return None

    def add_document_hash(self, file_path: str, file_hash: str) -> None:
        """
        Add a document hash to the database.

        Args:
            file_path (str): The file path of the document
            file_hash (str): The file hash of the document
        """
        self._store.mset([
            (file_path, file_hash)
        ])