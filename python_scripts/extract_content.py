import os
from bs4 import BeautifulSoup
import json

def extract_html_content(file_path):
    """
    Extracts structured content from a KBA or Application Process HTML file.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    extracted_data = {
        "title": soup.find('h1', class_='kb-title').get_text(strip=True) if soup.find('h1', class_='kb-title') else "N/A",
        "subtitle": soup.find('p', class_='kb-subtitle').get_text(strip=True) if soup.find('p', class_='kb-subtitle') else "N/A",
        "metadata": {},
        "sections": []
    }

    # Extract metadata
    metadata_div = soup.find('div', class_='kb-metadata')
    if metadata_div:
        for item in metadata_div.find_all('div', class_='kb-meta-item'):
            label = item.find('span', class_='kb-meta-label')
            value = item.find('span', class_='kb-meta-value')
            if label and value:
                extracted_data["metadata"][label.get_text(strip=True).replace(':', '')] = value.get_text(strip=True)

    # Extract sections
    for section in soup.find_all('div', class_='kb-section'):
        section_title_tag = section.find('h2', class_='kb-section-title')
        section_title = section_title_tag.get_text(strip=True) if section_title_tag else "Untitled Section"
        
        section_content = []
        for element in section.children:
            if element.name == 'p':
                section_content.append(element.get_text(strip=True))
            elif element.name == 'ul' or element.name == 'ol':
                list_items = []
                for li in element.find_all('li'):
                    list_items.append(li.get_text(strip=True))
                section_content.append({"list": list_items})
            elif element.name == 'div' and 'kb-alert' in element.get('class', []):
                alert_title = element.find('div', class_='kb-alert-title')
                alert_text = element.get_text(strip=True).replace(alert_title.get_text(strip=True), '', 1).strip() if alert_title else element.get_text(strip=True)
                section_content.append({"alert": {"title": alert_title.get_text(strip=True) if alert_title else "Alert", "content": alert_text}})
            elif element.name == 'div' and 'kb-code' in element.get('class', []):
                section_content.append({"code": element.get_text(strip=True)})
            elif element.name == 'table':
                table_data = []
                headers = [th.get_text(strip=True) for th in element.find_all('th')]
                table_data.append(headers)
                for row in element.find_all('tr')[1:]: # Skip header row
                    cols = [td.get_text(strip=True) for td in row.find_all('td')]
                    table_data.append(cols)
                section_content.append({"table": table_data})

        extracted_data["sections"].append({
            "title": section_title,
            "content": section_content
        })
    
    return extracted_data

if __name__ == "__main__":
    completed_docs_dir = "completed_documents"
    output_dir = "extracted_json"
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(completed_docs_dir):
        if filename.endswith(".html"):
            file_path = os.path.join(completed_docs_dir, filename)
            print(f"Processing {filename}...")
            extracted_content = extract_html_content(file_path)
            
            output_filename = os.path.splitext(filename)[0] + ".json"
            output_file_path = os.path.join(output_dir, output_filename)
            
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(extracted_content, f, indent=2, ensure_ascii=False)
            print(f"Extracted content saved to {output_file_path}")

    print("\nTo run this script, you need to install BeautifulSoup4:")
    print("pip install beautifulsoup4")
