import pathlib
from langchain_community.document_loaders import UnstructuredMarkdownLoader, PyPDFLoader, UnstructuredWordDocumentLoader
from langchain_core.documents import Document

def read_file(file_path: str) -> list[Document]:
    file_extension = pathlib.Path(file_path).suffix

    loader = None
    if file_extension == '.md':
        loader = UnstructuredMarkdownLoader(file_path)
    elif file_extension == '.pdf':
        loader = PyPDFLoader(file_path)
    elif file_extension in ['.doc', '.docx']:
        loader = UnstructuredWordDocumentLoader(file_path)

    if not loader:
        raise ValueError(f"{file_extension} is not supported.")
    
    result = loader.load()

    return result
