# Project Decisions Log

## 2025-07-16 - Initial Setup and Document Storage

**Decision:** To create a dedicated Markdown file (`decisions.md`) for logging key project decisions and a `completed_documents` directory to store finalized HTML articles, application processes, and user guides. These completed documents will serve as the input for the RAG system's data chunking process.

**Reasoning:** Centralized decision logging ensures transparency, traceability, and provides a historical record of project evolution. A dedicated directory for completed documents streamlines the RAG ingestion pipeline by clearly separating source templates from finalized content.

## 2025-07-16 - Document Template Refinement and RAG System Preparation

**Decisions Made:**

1.  **Template Renaming:** Renamed `index.html` to `article-template.html` and `applications.html` to `application-process-template.html` to clearly denote their purpose as templates.
2.  **New Template Creation:** Created additional HTML templates for:
    *   `user-guide-template.html` (for detailed instructions and how-to guides)
    *   `faq-template.html` (for frequently asked questions)
    *   `system-overview-template.html` (for high-level system/application descriptions)
    *   `onboarding-checklist-template.html` (for onboarding procedures)
3.  **Example Document Setup:** Created example HTML files (`article-example.html`, `application-process-example.html`) within the `completed_documents` directory to serve as test data for the RAG ingestion pipeline.
4.  **HTML Content Extraction Script (`extract_content.py`):** Developed a Python script to parse HTML documents, extract text content from defined sections (e.g., titles, paragraphs, lists, tables, code blocks, alerts), and structure it into a JSON format. This script prepares the raw text for subsequent chunking and embedding.
5.  **Text Chunking and Embedding Script (`generate_embeddings.py`):** Developed a Python script that utilizes `langchain`'s `RecursiveCharacterTextSplitter` for intelligent text chunking (with a `chunk_size=500` and `chunk_overlap=50`) and `sentence-transformers` (`all-MiniLM-L6-v2` model) for generating vector embeddings for each text chunk. This script outputs a JSON file containing chunks, their metadata, and embeddings.
6.  **Vector Database Population Script (`populate_vector_db.py`):** Developed a Python script to initialize and populate a ChromaDB instance (`kba_rag_collection`) with the generated text chunks, their embeddings, and associated metadata. ChromaDB was chosen for its lightweight nature and suitability for local VM deployment.
7.  **Local LLM and RAG Query Flow Strategy:** Outlined the conceptual architecture for integrating a local LLM (e.g., Gemma, Mistral, Llama 3 via Ollama, LM Studio, or Text Generation WebUI) with the vector database for a RAG system. This includes steps for query embedding, vector search, context construction, and LLM prompting.

## 2025-07-16 - Repository Organization and Cleanup

**Decisions Made:**

1.  **Directory Creation:** Created two new directories: `templates` to house all HTML template files and `python_scripts` to store all Python scripts related to the RAG system data preparation.
2.  **File Relocation:** Moved all `*-template.html` files into the `templates` directory. Moved `extract_content.py`, `generate_embeddings.py`, and `populate_vector_db.py` into the `python_scripts` directory. Relocated `document_embeddings.json` (containing generated embeddings) from the root to the `extracted_json` directory, as it is a processed output.

**Reasoning:** This reorganization improves repository clarity, maintainability, and makes it easier to locate specific file types. It also logically groups related components of the RAG system setup.

## 2025-07-16 - RAG System Debugging and Performance Improvements

**Decisions Made:**

1.  **Improved Example Content:** Updated `article-example.html` and `application-process-example.html` with more realistic and detailed help desk content to provide better training data for the RAG system.
2.  **Increased Retrieval Context:** Increased `n_results` in `python_scripts/query_rag.py` from 3 to 5 to allow the LLM to retrieve more relevant chunks from the vector database, providing richer context for responses.
3.  **Enhanced Content Extraction (`extract_content.py`):** Modified `extract_content.py` to improve the structural preservation of content, particularly for list items (separating bolded titles from descriptions) and tables, ensuring more meaningful data is passed to the chunking stage.
4.  **Refined Chunking and Flattening (`generate_embeddings.py`):** Updated `python_scripts/generate_embeddings.py` to leverage the improved structure from `extract_content.py` in its `flatten_content` function. Also, increased `chunk_size` to 700 and `chunk_overlap` to 70 to provide more comprehensive chunks for embedding.
5.  **Resolved Script Errors:** Debugged and fixed `IndentationError` and `AttributeError` in `generate_embeddings.py` by correcting function definitions, calls, and ensuring the script properly excludes its own output file (`document_embeddings.json`) during processing.
6.  **Full RAG Pipeline Re-execution:** Systematically re-ran `extract_content.py`, `generate_embeddings.py`, and `populate_vector_db.py` after each significant modification to ensure the ChromaDB was updated with the latest, most accurate data.

**Outcome:** These iterative improvements led to significantly better RAG system performance, with the LLM now providing accurate and contextually relevant answers for previously failing queries.

**Future Steps:**

1.  **Choose and Set Up Local LLM:** Select and configure a local LLM and serving framework.
2.  **Develop Query Application:** Build an application to interact with the RAG system (query, retrieve, prompt LLM, display response).