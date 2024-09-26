import argparse
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from embedding_models.get_ollama_embedding_model import get_ollama_embedding_model
from stores.chroma_vector_store import ChromaVectorStore
from stores.document_hashes_store import DocumentHashesStore
from stores.document_store import DocumentStore
from stores.sqlite_store import SqliteStore
from utils.read_file import read_file
from utils.verbose_print import verbose_print
from utils.env import get_child_chunk_size, get_chroma_path, get_document_store_path, get_parent_chunk_size, get_parent_doc_id_key, get_wiki_dir
from utils.get_document_with_metadata import get_document_with_metadata
from utils.get_hash import get_file_hash
from utils.get_files_in_directory import get_files_in_directory
from utils.split_list_into_chunks import split_list_into_chunks
from dotenv import load_dotenv

load_dotenv()

def main() -> None:
    """
    Main function to handle database reset and document processing.

    This function performs the following tasks:
    1. Parse command-line arguments
    2. Reset the database if requested
    3. Load documents from the wiki directory
    4. Process each document:
       - Check if it's new or updated
       - Split the document into chunks and sub-chunks
       - Add the document and its chunks to the vector store and document store
    5. Update the document hash store
    """
    args = parse_arguments()
    if args.reset:
        print("✨ Clearing Database")
        clear_database()

    # Load, split, and add documents to the database
    wiki_dir: str = get_wiki_dir()
    wiki_pages_paths: list[str] = get_files_in_directory(wiki_dir, ['.md', '.pdf', '.doc', '.docx'], ['.attachments/', '.git/'])

    verbose_print(f"{len(wiki_pages_paths)} documents found in the '{wiki_dir}'")

    document_hash_store = DocumentHashesStore()
    for wiki_page_path in wiki_pages_paths:
        local_file_hash: str = get_file_hash(wiki_page_path)
        document_hash: str = document_hash_store.get_document_hash(wiki_page_path)

        if local_file_hash == document_hash:
            verbose_print(f"Skipping {wiki_page_path} because it already exists in the database")
            continue
        elif not document_hash:
            verbose_print(f"Adding {wiki_page_path} because it does not exist in the database")
        else:
            verbose_print(f"Updating {wiki_page_path} because it's a new version.")

        documents: list[Document] = read_file(wiki_page_path)

        verbose_print("Splitting document into chunks...")
        parent_chunk_size: int = get_parent_chunk_size()
        child_chunk_size: int = get_child_chunk_size()
        docs, sub_docs = split_documents(documents, parent_chunk_size, child_chunk_size)

        verbose_print("Adding document and chunks to vector- and document store...")
        add_documents_to_store(docs, sub_docs)

        document_hash_store.add_document_hash(wiki_page_path, local_file_hash)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Process documents and manage the database.")
    parser.add_argument("--reset", action="store_true", help="Reset the database before processing.")
    return parser.parse_args()

def split_documents(
    documents: list[Document],
    parent_chunk_size: int = 400,
    child_chunk_size: int = 0
) -> tuple[list[Document], list[Document]]:
    """
    Split documents into chunks and sub-chunks.

    Args:
        documents (list[Document]): List of documents to split.
        parent_chunk_size (int, optional): Size of parent chunks. Defaults to 400.
        child_chunk_size (int, optional): Size of child chunks. If 0, no sub-chunks are created. Defaults to 0.

    Returns:
        tuple[list[Document], list[Document]]: A tuple containing two lists:
            1. List of parent documents (chunks)
            2. List of child documents (sub-chunks), empty if child_chunk_size is 0
    """
    parent_text_splitter = RecursiveCharacterTextSplitter(chunk_size=parent_chunk_size)
    parent_doc_id_key = get_parent_doc_id_key()

    new_documents = get_document_with_metadata(parent_text_splitter.split_documents(documents))
    sub_documents = []

    if child_chunk_size > 0:
        child_text_splitter = RecursiveCharacterTextSplitter(chunk_size=child_chunk_size)
        for idx, document in enumerate(new_documents):
            _sub_documents = get_document_with_metadata(
                child_text_splitter.split_documents([document]),
                idx
            )
            for sub_document in _sub_documents:
                sub_document.metadata[parent_doc_id_key] = document.metadata.get("id")
                sub_documents.append(sub_document)

    return new_documents, sub_documents

def add_documents_to_store(
        documents: list[Document],
        sub_documents: list[Document] = [],
        chunk_size: int = 500
) -> None:
    """
    Add documents to the vector store and document store.

    Args:
        documents (list[Document]): List of parent documents to add to the document store.
        sub_documents (list[Document], optional): List of sub-documents to add to the vector store. 
            If empty, parent documents are added to the vector store instead. Defaults to [].
        chunk_size (int, optional): Number of documents to process in each batch. Defaults to 500.
    """
    document_store = DocumentStore()
    vector_store = ChromaVectorStore(get_ollama_embedding_model())
    documents_for_vector_store = sub_documents if sub_documents else documents

    if sub_documents:
        document_store.add_documents(documents)

    existing_ids = vector_store.get_document_ids()
    verbose_print(f"\tNumber of existing documents in vector store: {len(existing_ids)}")

    documents_to_add, documents_to_update = get_documents_to_add_or_update(documents_for_vector_store, existing_ids, vector_store)

    if documents_to_add:
        verbose_print(f"\t👉 Adding {len(documents_to_add)} documents")
        add_or_update_documents_to_vectorstore(documents_to_add, vector_store, chunk_size)
    else:
        verbose_print("\t✅ No new documents to add")

    if documents_to_update:
        verbose_print(f"\t👉 Updating {len(documents_to_update)} documents")
        add_or_update_documents_to_vectorstore(documents_to_update, vector_store, chunk_size)
    else:
        verbose_print("\t✅ Documents are already up-to-date")

def get_documents_to_add_or_update(
        documents: list[Document],
        existing_ids: list[str],
        vector_store: ChromaVectorStore
) -> tuple[list[Document], list[Document]]:
    """
    Determine which documents need to be added or updated in the vector store.

    Args:
        documents (list[Document]): List of documents to process.
        existing_ids (list[str]): List of document IDs already in the vector store.
        vector_store (ChromaVectorStore): The vector store instance.

    Returns:
        tuple[list[Document], list[Document]]: A tuple containing two lists:
            1. List of new documents to be added
            2. List of existing documents to be updated
    """
    new_documents = []
    updated_documents = []

    for document in documents:
        id = document.metadata["id"]
        hash = document.metadata["hash"]

        if id not in existing_ids:
            new_documents.append(document)
        else:
            existing_doc = vector_store.get_documents_by_ids(ids=[id])
            if existing_doc and existing_doc["metadatas"][0].get("hash", "") != hash:
                updated_documents.append(document)

    return new_documents, updated_documents

def add_or_update_documents_to_vectorstore(
        documents: list[Document],
        vector_store: ChromaVectorStore,
        chunk_size: int = 500
) -> None:
    """
    Add or update documents in the vector store in batches.

    Args:
        documents (list[Document]): List of documents to add or update.
        vector_store (ChromaVectorStore): The vector store instance.
        chunk_size (int, optional): Number of documents to process in each batch. Defaults to 500.
    """
    chunks = split_list_into_chunks(documents, chunk_size)
    for idx, chunk_group in enumerate(chunks):
        vector_store.add_documents(chunk_group)
        verbose_print(f"\t👉 Added/Updated: {chunk_size * idx + len(chunk_group)}")

def clear_database() -> None:
    """
    Clear both the Chroma vector store and the document store databases.

    This function removes all data from the specified database paths for both
    the Chroma vector store and the SQLite document store.
    """
    ChromaVectorStore.clear(get_chroma_path())
    SqliteStore.clear(get_document_store_path())

if __name__ == "__main__":
    main()