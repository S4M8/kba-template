import chromadb
import json
import os

def populate_chroma_db(embeddings_file, db_path="chroma_db"):
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path=db_path)

    # Get or create a collection
    collection_name = "kba_rag_collection"
    try:
        collection = client.get_collection(name=collection_name)
        print(f"Collection '{collection_name}' already exists. Adding new data.")
    except:
        collection = client.create_collection(name=collection_name)
        print(f"Collection '{collection_name}' created.")

    # Load embeddings data
    with open(embeddings_file, 'r', encoding='utf-8') as f:
        embeddings_data = json.load(f)

    # Prepare data for ChromaDB
    ids = []
    embeddings = []
    documents = []
    metadatas = []

    for item in embeddings_data:
        ids.append(item["chunk_id"])
        embeddings.append(item["embedding"])
        documents.append(item["chunk_text"])
        metadatas.append({
            "document_title": item["document_title"],
            "document_id": item["document_id"],
            "section_title": item["section_title"]
        })

    # Add to collection
    # ChromaDB has a batch size limit, so we might need to chunk this
    batch_size = 100
    for i in range(0, len(ids), batch_size):
        batch_ids = ids[i:i+batch_size]
        batch_embeddings = embeddings[i:i+batch_size]
        batch_documents = documents[i:i+batch_size]
        batch_metadatas = metadatas[i:i+batch_size]

        collection.add(
            embeddings=batch_embeddings,
            documents=batch_documents,
            metadatas=batch_metadatas,
            ids=batch_ids
        )
        print(f"Added batch {i//batch_size + 1} to ChromaDB.")

    print(f"Successfully populated ChromaDB collection '{collection_name}' with {len(ids)} chunks.")

if __name__ == "__main__":
    embeddings_input_file = "extracted_json\document_embeddings.json"
    populate_chroma_db(embeddings_input_file)
    print("\nRemember to install chromadb: pip install chromadb")
