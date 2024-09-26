from langchain_community.embeddings.ollama import OllamaEmbeddings


def get_ollama_embedding_model() -> OllamaEmbeddings:
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return embeddings
