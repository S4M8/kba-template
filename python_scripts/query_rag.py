import chromadb
import json
from sentence_transformers import SentenceTransformer
import requests
import os

def query_rag_system(query_text, db_path="chroma_db", model_name="all-MiniLM-L6-v2", ollama_url="http://localhost:11434/api/generate"):
    # 1. Load Embedding Model
    embedding_model = SentenceTransformer(model_name)

    # 2. Connect to ChromaDB
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(name="kba_rag_collection")

    # 3. Generate Embedding for Query
    query_embedding = embedding_model.encode(query_text).tolist()

    # 4. Perform Similarity Search in ChromaDB
    # Retrieve top N most relevant chunks
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5,  # Increased to 5 to get more context
        include=['documents', 'metadatas']
    )

    retrieved_chunks = []
    if results and results['documents']:
        for i in range(len(results['documents'][0])):
            chunk_text = results['documents'][0][i]
            metadata = results['metadatas'][0][i]
            retrieved_chunks.append({
                "text": chunk_text,
                "metadata": metadata
            })

    if not retrieved_chunks:
        print("No relevant documents found in the knowledge base.")
        return "I could not find relevant information in the knowledge base to answer your question."

    # 5. Construct Prompt for LLM
    context = "\n\n".join([chunk["text"] for chunk in retrieved_chunks])
    
    # Add metadata to context for better grounding
    metadata_info = []
    for chunk in retrieved_chunks:
        meta = chunk["metadata"]
        metadata_info.append(f"Document: {meta.get('document_title', 'N/A')}, Section: {meta.get('section_title', 'N/A')}")
    context += "\n\nSource Information:\n" + "\n".join(metadata_info)

    prompt = f"""Using only the following context, answer the question. If the answer is not in the context, state that you don't have enough information.

Context:
{context}

Question: {query_text}
Answer:"""

    # 6. Send Prompt to Local LLM (Ollama API)
    headers = {'Content-Type': 'application/json'}
    data = {
        "model": "llama3",  # Or "gemma:2b" or whatever model you downloaded
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(ollama_url, headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for HTTP errors
        llm_response = response.json()['response']
        return llm_response
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to Ollama. Please ensure Ollama is running and the model is loaded."
    except requests.exceptions.RequestException as e:
        return f"Error querying Ollama: {e}"

if __name__ == "__main__":
    # Example usage:
    user_query = input("Enter your query: ")
    response = query_rag_system(user_query)
    print("\nLLM Response:")
    print(response)
