import os
import json
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter

def flatten_content(content_list, section_title):
    flat_text = []
    for item in content_list:
        if isinstance(item, str):
            flat_text.append(item)
        elif isinstance(item, dict):
            if "list" in item:
                # Add a heading for lists if it's part of a solution/process
                if "Solution" in section_title or "Process" in section_title:
                    flat_text.append("Step-by-Step Instructions:")
                for li_item in item["list"]:
                    flat_text.append(f"{li_item["title"]}: {li_item["description"]}")
            elif "alert" in item:
                flat_text.append(item["alert"]["title"] + ": " + item["alert"]["content"])
            elif "code" in item:
                flat_text.append("Code Example:\n" + item["code"])
            elif "table" in item:
                # Format table content for better readability, including headers with each row
                table_str = ""
                headers = item["table"][0] # First row is headers
                for row_idx, row in enumerate(item["table"]):
                    if row_idx == 0: continue # Skip headers as they are handled below
                    row_data = []
                    for col_idx, cell in enumerate(row):
                        row_data.append(f"{headers[col_idx]}: {cell}")
                    table_str += "; ".join(row_data) + "\n"
                flat_text.append("Table Data:\n" + table_str.strip())
    return "\n\n".join(flat_text)

def generate_embeddings_for_documents(json_dir, model_name="all-MiniLM-L6-v2"):
    model = SentenceTransformer(model_name)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700, # Increased chunk size
        chunk_overlap=70, # Increased overlap
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )

    all_chunks_with_metadata = []

    for filename in os.listdir(json_dir):
        if filename.endswith(".json") and filename != "document_embeddings.json":
            file_path = os.path.join(json_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                doc_data = json.load(f)

            doc_title = doc_data.get("title", "Untitled Document")
            doc_id = doc_data["metadata"].get("Article ID", doc_data["metadata"].get("Process ID", "N/A"))

            for section in doc_data.get("sections", []):
                section_title = section.get("title", "Untitled Section")
                # Pass section_title to flatten_content for conditional heading
                flat_section_text = flatten_content(section.get("content", []), section_title)

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