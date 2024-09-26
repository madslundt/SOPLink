import os


def get_verbose() -> bool:
    return os.getenv('VERBOSE', 'false').lower() == 'true'

def get_wiki_dir() -> str:
    return os.getenv('WIKI_PATH', 'wiki/')

def get_document_store_path() -> str:
    return os.getenv('DOCUMENT_STORE_PATH', 'docstore/')

def get_document_hashes_table_name() -> str:
    return os.getenv('DOCUMENT_HASHES_TABLE_NAME', 'document_hashes')

def get_document_store_table_name() -> str:
    return os.getenv('DOCUMENT_STORE_TABLE_NAME', 'documents')

def get_parent_chunk_size() -> int:
    return int(os.getenv('PARENT_CHUNK_SIZE', '3000'))

def get_child_chunk_size() -> int:
    return int(os.getenv('CHILD_CHUNK_SIZE', '400'))

def get_parent_doc_id_key() -> str:
    return os.getenv('PARENT_DOC_ID_KEY', 'doc_id')

def get_chroma_path() -> str:
    return os.getenv('CHROMA_PATH', 'chroma')

def get_chroma_collection_name() -> str:
    return os.getenv('CHROMA_COLLECTION_NAME', 'documents')

def get_chat_brd_username() -> str:
    return os.getenv('CHAT_BRD_USERNAME', '')

def get_chat_brd_secret_key() -> str:
    return os.getenv('CHAT_BRD_SECRET_KEY', '')

def get_chat_brd_chatbot_pk() -> str:
    return os.getenv('CHAT_BRD_CHATBOT_PK', 'static')

def get_chat_brd_chatbot_sk() -> str:
    return os.getenv('CHAT_BRD_CHATBOT_SK', 'gpt-4o')

def get_chat_brd_cert_pem() -> str:
    return os.getenv('CHAT_BRD_CERT_PEM', '')

def get_chat_brd_base_url() -> str:
    return os.getenv('CHAT_BRD_BASE_URL', '')
