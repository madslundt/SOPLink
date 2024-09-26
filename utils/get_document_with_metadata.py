from typing import Optional
from langchain_core.documents import Document

from utils.get_hash import get_content_hash

def get_document_with_metadata(documents: list[Document], source_chunk_idx: Optional[int] = None) -> list[Document]:
    """
    Generate metadata for documents, including unique IDs and hash.

    Args:
        documents (list[Document]): List of documents to generate metadata for.
        source_chunk_idx (Optional[int], default None): Index of the source chunk, if applicable.

    Returns:
        list[Document]: List of documents with updated metadata.
    """
    last_page_id = None
    current_chunk_index = 0

    for document in documents:
        source = document.metadata.get("source")
        page = document.metadata.get("page")
        current_page_id = f"{source}"
        if source_chunk_idx is not None:
            current_page_id += f":{source_chunk_idx}"

        if page is not None:
            current_page_id += f":{page}"

        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        id = f"{current_page_id}:{current_chunk_index}"
        document.metadata["id"] = id
        document.metadata["hash"] = get_content_hash(document.page_content)
        last_page_id = current_page_id

    return documents