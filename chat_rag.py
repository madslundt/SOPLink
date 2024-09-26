import argparse
from textwrap import dedent
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_core.runnables import Runnable
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain.retrievers.multi_vector import MultiVectorRetriever

from embedding_models.get_ollama_embedding_model import get_ollama_embedding_model
from llm_models.chat_brd import ChatBRD
from stores.chroma_vector_store import ChromaVectorStore
from stores.document_store import DocumentStore
from utils.env import get_chat_brd_base_url, get_chat_brd_chatbot_pk, get_chat_brd_chatbot_sk, get_chat_brd_secret_key, get_chat_brd_username, get_parent_doc_id_key
from dotenv import load_dotenv

load_dotenv()

def main() -> None:
    """
    Main function to handle command-line arguments and start the interactive query loop.

    This function sets up the argument parser and initiates the interactive query loop
    where users can input queries and receive responses based on the RAG (Retrieval-Augmented Generation) system.
    """
    parser = argparse.ArgumentParser(description="Interactive RAG-based query system")
    parser.add_argument("--query_text", type=str, help="Initial query text (optional)")
    args = parser.parse_args()

    if args.query_text:
        print(f"Initial query: {args.query_text}")

    interactive_query_loop()

def get_contextualize_question_prompt() -> ChatPromptTemplate:
    """
    Create a prompt template for contextualizing questions based on chat history.

    Returns:
        ChatPromptTemplate: A prompt template that reformulates user questions
        considering the chat history context.
    """
    contextualize_q_system_prompt = dedent("""
        Given a chat history and the latest user question
        which might reference context in the chat history,
        formulate a standalone question which can be understood
        without the chat history. Do NOT answer the question, just
        reformulate it if needed and otherwise return it as is.
    """)

    return ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

def get_question_answering_prompt() -> ChatPromptTemplate:
    """
    Create a prompt template for answering questions using retrieved context.

    Returns:
        ChatPromptTemplate: A prompt template that guides the model to answer
        questions concisely using the provided context.
    """
    qa_system_prompt = dedent("""
        You are an assistant for question-answering tasks. Use
        the following pieces of retrieved context to answer the
        question. If you don't know the answer, just say that you
        don't know. Use three sentences maximum and keep the answer
        concise.

        {context}
    """)

    return ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

def get_rag_chain() -> Runnable:
    """
    Create a Retrieval-Augmented Generation (RAG) chain for question answering.

    This function sets up the complete RAG pipeline, including:
    1. Initializing the language model and vector store
    2. Creating a multi-vector retriever
    3. Setting up a history-aware retriever
    4. Combining the retriever with a question-answering chain

    Returns:
        Runnable: A RAG chain that can process queries and return answers
        based on retrieved context.
    """
    llm = get_llm()

    vector_store = ChromaVectorStore(get_ollama_embedding_model())
    document_store = DocumentStore()
    retriever = MultiVectorRetriever(
        vectorstore=vector_store.get_store(),
        docstore=document_store.get_store(),
        id_key=get_parent_doc_id_key(),
        search_type="similarity",
        search_kwargs={"k": 3},
    )

    contextualize_q_prompt = get_contextualize_question_prompt()
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    qa_prompt = get_question_answering_prompt()
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    return create_retrieval_chain(history_aware_retriever, question_answer_chain)

def interactive_query_loop() -> None:
    """
    Run an interactive loop for user queries using the RAG chain.

    This function allows users to input queries and receive answers based on
    the RAG system. It maintains a chat history and provides options to:
    - Exit the loop ('exit' or 'q')
    - Reset the chat history ('reset' or 'r')
    - View the chat history ('chat_history', 'ch', or 'history')

    The function processes each query, updates the chat history, and displays
    the answer along with the sources of information used.
    """
    rag_chain = get_rag_chain()
    chat_history: list[BaseMessage] = []

    while True:
        query = input("\nQuery: ").strip()
        if query.lower() in {"exit", "q"}:
            break
        if query.lower() in {"reset", "r"}:
            chat_history = []
            print(chr(27) + "[2J")  # Clear terminal
            print("Chat history has been reset")
            continue
        if query.lower() in {"chat_history", "ch", "history"}:
            messages = "\n".join([f"{'You' if isinstance(message, HumanMessage) else 'AI'}: \"{message.content}\"" for message in chat_history])
            print(chr(27) + "[2J")  # Clear terminal
            print(f"Chat history:\n\033[92m{messages}\033[0m\n")
            continue
        if query:
            result = rag_chain.invoke({"input": query, "chat_history": chat_history})

            print(result["answer"])
            print("Sources: ", [f"{c.metadata['source']}" for c in result["context"]])

            chat_history.append(HumanMessage(content=query))
            chat_history.append(AIMessage(content=result["answer"]))

def get_llm() -> ChatBRD:
    """
    Initialize and return a ChatBRD language model instance.

    Returns:
        ChatBRD: An instance of the ChatBRD language model configured with
        environment-specific credentials.
    """
    return ChatBRD(
        username=get_chat_brd_username(),
        secret_key=get_chat_brd_secret_key(),
        base_url=get_chat_brd_base_url(),
        chatbot_pk="static",
        chatbot_sk="gpt-4o",
    )

if __name__ == "__main__":
    main()
