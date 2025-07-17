import os
import json
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter

def flatten_content(content_list):
    flat_text = []
    for item in content_list:
        if isinstance(item, str):
            flat_text.append(item)
        elif isinstance(item, dict):
            if "list" in item:
                flat_text.extend(item["list"])
            elif "alert" in item:
                flat_text.append(item["alert"]["title"] + ": " + item["alert"]["content"])
            elif "code" in item:
                flat_text.append(item["code"])
            elif "table" in item:
                flat_text.append(" ".join([" ".join(row) for row in item["table"]]))
    return "\n\n".join(flat_text)

def generate_embeddings_for_documents(json_dir, model_name="all-MiniLM-L6-v2"):
    model = SentenceTransformer(model_name)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )

    all_chunks_with_metadata = []

    for filename in os.listdir(json_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(json_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                doc_data = json.load(f)

            doc_title = doc_data.get("title", "Untitled Document")
            doc_id = doc_data["metadata"].get("Article ID", doc_data["metadata"].get("Process ID", "N/A"))

            for section in doc_data.get("sections", []):
                section_title = section.get("title", "Untitled Section")
                flat_section_text = flatten_content(section.get("content", []))

                if flat_section_text: # Only process if there's content
                    chunks = text_splitter.split_text(flat_section_text)
                    for i, chunk_text in enumerate(chunks):
                        embedding = model.encode(chunk_text).tolist() # Convert numpy array to list for JSON serialization
                        all_chunks_with_metadata.append({
                            "document_title": doc_title,
                            "document_id": doc_id,
                            "section_title": section_title,
                            "chunk_text": chunk_text,
                            "chunk_id": f"{doc_id}-{section_title.replace(' ', '_')}-{i}", # Unique ID for each chunk
                            "embedding": embedding
                        })
    return all_chunks_with_metadata

if __name__ == "__main__":
    json_input_dir = "extracted_json"
    output_embeddings_file = "extracted_json\document_embeddings.json"

    print("Generating embeddings...")
    embeddings_data = generate_embeddings_for_documents(json_input_dir)

    with open(output_embeddings_file, 'w', encoding='utf-8') as f:
        json.dump(embeddings_data, f, indent=2, ensure_ascii=False)

    print(f"Embeddings and metadata saved to {output_embeddings_file}")
    print("\nRemember to install sentence-transformers: pip install sentence-transformers")
    print("And langchain: pip install langchain")