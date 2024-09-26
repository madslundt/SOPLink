# SOPLink
SOPLink captures the core functionality of linking SOP (Standard Operating Procedure) documents with a structured JSON format. This integration enables seamless communication between SOPs and the system, facilitating the verification of results.

The project consist of different areas:
 - RAG using Langchain with custom LLM
 - SOP to JSON using Langgraph and custom LLM
 - Convert SOPs to markdown

## RAG
This part implements a comprehensive Retrieval-Augmented Generation (RAG) system, consisting of two main components: a document processing pipeline and an interactive query interface.

RAG is an AI technique that enhances language models by retrieving relevant information from a knowledge base before generating responses. This approach combines the benefits of retrieval-based systems (which can access large amounts of specific information) with the flexibility of generative models.

The document processing pipeline handles the ingestion of documents from a specified directory, processes them by splitting into chunks, and stores them in vector and document stores. It includes functionality for updating existing documents, managing document hashes, and efficiently handling large numbers of documents through batched processing. The pipeline is flexible, allowing for both parent and child document chunking, and integrates with various storage systems including Chroma vector store and SQLite document store.

The interactive query interface sets up a conversational system where users can input queries and receive AI-generated responses based on retrieved context. It utilizes a multi-vector retriever, a history-aware retriever, and a question-answering chain to process queries. The system maintains a chat history and offers features like resetting the conversation, viewing chat history, and exiting the loop.

Both components are built using the LangChain library, incorporating prompt templates for contextualizing questions and answering based on retrieved documents. The system also integrates with a custom ChatBRD language model, configured with environment-specific credentials.

Key features of the entire system include command-line argument parsing, database reset capabilities, verbose logging options, and an efficient RAG chain construction that enhances the quality and relevance of AI-generated responses by leveraging a knowledge base of processed documents.


## SOP to JSON
This part implements a document processing and information extraction system using LangGraph, a powerful library for building complex AI workflows. The system consists of a structured pipeline for analyzing documents and extracting specific information in a modular, graph-based approach.

LangGraph, a graph-based framework for AI applications, is at the core of this implementation. It allows for the creation of a flexible and modular workflow, represented as a directed graph of interconnected processing nodes. This approach enables efficient handling of complex document analysis tasks, with each node in the graph performing a specific function in the overall process.

The document processing pipeline, built using LangGraph's StateGraph, manages the flow of information through various stages. It begins with document preparation, followed by targeted extraction of specific sections (such as 'samples' and 'SST'), and then converts these sections into structured JSON format. This pipeline demonstrates LangGraph's ability to orchestrate multiple AI operations in a coherent, sequential manner.

A key feature of this system is its integration with the ChatBRD language model, which is utilized at different stages of the workflow for natural language understanding and generation tasks. The system is configured to use specific ChatBRD models for different extraction and conversion tasks, showcasing the flexibility of LangGraph in incorporating external AI services.

## Convert SOPs to markdown
This part implements Word-to-Markdown Conversion Utility.
Complementing the main analysis pipeline, this script automates the conversion of Word documents (.doc, .docx) to Markdown format. It processes files in a specified directory, converts them to Markdown, and then reformats the resulting Markdown files. This utility enhances the system's capability to handle various document formats, preparing them for further analysis in the main pipeline.


## Setup
1. Install dependencies
```sh
pipenv install
```

2. Setup environment variables
Copy `.env.example` to `.env` and update it with your changes (including secrets)

3. Enter virtual environment
```sh
pipenv shell
```

*To exit the shell input `exit`*

### Setup RAG
1. Clone Wiki pages to `wiki/`


2. Populate vector store
```sh
python populate_database.py
```

*To clear the database before populating input `--reset`*

3. Start application
```sh
python chat_rag.py
```

*To exit the rag input `q`*
*To reset chat history input `r`*
*To show chat history `ch`*


### Setup SOP to JSON
1. Update `DOCUMENT_PATH` in **run_graph.py**

2. Run graph
```sh
python run_graph.py
```

*Run also generates `graph/graph.md` with a mermaid diagram of the graph*
