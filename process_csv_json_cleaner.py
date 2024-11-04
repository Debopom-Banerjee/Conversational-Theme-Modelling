import os
import json
import csv
import re
from google.colab import files  # Add this import

def clean_text(text):
    """Cleans text by removing unnecessary spaces, line breaks, and fixing encoding issues."""
    if not isinstance(text, str):
        return text
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text

def load_csv(csv_file):
    """Loads the CSV file and extracts the ID column."""
    try:
        # Print current directory contents for debugging
        print(f"Current directory contents: {os.listdir()}")
        print(f"Attempting to load CSV file: {csv_file}")
        
        with open(csv_file, mode='r') as file:
            csv_reader = csv.reader(file)
            ids = [row[0].strip() for row in csv_reader]  # Clean the IDs
            print(f"Successfully loaded {len(ids)} IDs from CSV")
        return ids
    except FileNotFoundError:
        print(f"CSV file not found: {csv_file}")
        print("Please make sure the file is uploaded to Colab")
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {str(e)}")
    return []

def process_json_file(json_file, valid_ids):
    """Processes a single JSON file, cleaning data and extracting necessary fields."""
    try:
        print(f"Processing file: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        doc_id = data.get("docId", "").strip()
        if doc_id in valid_ids:
            metadata = data.get('metadata', {})
            
            title = clean_text(metadata.get('title', ''))
            authors = metadata.get('authors', [])
            
            authors_cleaned = [
                f"{author['first']} {author['last']}".strip() for author in authors
            ]
            
            abstract_data = data.get('abstract', [])
            if isinstance(abstract_data, list):
                abstract = " ".join([clean_text(sentence.get('sentence', '')) for sentence in abstract_data])
            elif isinstance(abstract_data, str):
                abstract = clean_text(abstract_data)
            else:
                abstract = ""

            bib_entries = data.get('bib_entries', {})
            
            return {
                'docId': doc_id,
                'title': title,
                'authors': ", ".join(authors_cleaned),
                'abstract': abstract,
                'bib_entries': bib_entries,
            }
    except Exception as e:
        print(f"Error processing {json_file}: {str(e)}")
    return None

def process_json_folder(folder_path, valid_ids):
    """Iterates through all JSON files in the folder and processes each one."""
    cleaned_data = []
    try:
        # Print folder contents for debugging
        print(f"Contents of {folder_path}: {os.listdir(folder_path)}")
        
        for json_file in os.listdir(folder_path):
            if json_file.endswith('.json'):
                json_path = os.path.join(folder_path, json_file)
                result = process_json_file(json_path, valid_ids)
                if result:
                    cleaned_data.append(result)
                    print(f"Successfully processed: {json_file}")
    except Exception as e:
        print(f"Error accessing folder {folder_path}: {str(e)}")
    
    return cleaned_data

def save_to_csv(data, output_csv_file):
    """Saves the cleaned data to a CSV file, converting bib_entries to a string."""
    if data:
        fieldnames = ['docId', 'title', 'authors', 'abstract', 'bib_entries']

        for item in data:
            if 'bib_entries' in item:
                item['bib_entries'] = json.dumps(item['bib_entries'])

        with open(output_csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        print(f"Cleaned data has been saved to {output_csv_file}")
        # Download the file automatically in Colab
        files.download(output_csv_file)

def main():
    # Ensure the CSV file exists
    csv_file = '/content/Conversational theme modelling/os-ccby-40k-ids.csv'
    if not os.path.exists(csv_file):
        print(f"Please upload {csv_file} first")
        return
    
    valid_ids = load_csv(csv_file)
    if not valid_ids:
        print("No valid IDs were loaded from the CSV file. Exiting.")
        return
    
    # Process JSON files in the folder
    json_folder = '/content/Conversational theme modelling/train_data'
    if not os.path.isdir(json_folder):
        print(f"The folder {json_folder} does not exist. Creating it...")
        os.makedirs(json_folder)
        print("Please upload your JSON files to the 'test_data' folder")
        return
    
    cleaned_data = process_json_folder(json_folder, valid_ids)
    
    if cleaned_data:
        # Save and download output files
        output_json_file = '/content/Conversational theme modelling/clean_data.json'
        with open(output_json_file, 'w', encoding='utf-8') as outfile:
            json.dump(cleaned_data, outfile, ensure_ascii=False, indent=4)
        print(f"Cleaned data has been saved to {output_json_file}")
        files.download(output_json_file)
        
        output_csv_file = '/content/Conversational theme modelling/clean_data.csv'
        save_to_csv(cleaned_data, output_csv_file)
    else:
        print("No cleaned data was generated.")

if __name__ == "__main__":
    main()
