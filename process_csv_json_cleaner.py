import os
import json
import csv
import re

def clean_text(text):
    """Cleans text by removing unnecessary spaces, line breaks, and fixing encoding issues."""
    if not isinstance(text, str):
        return text
    text = text.strip()  # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces/newlines with single space
    return text

def load_csv(csv_file):
    """Loads the CSV file and extracts the ID column."""
    try:
        with open(csv_file, mode='r') as file:
            csv_reader = csv.reader(file)
            ids = [row[0].strip() for row in csv_reader]  # Clean the IDs
        return ids
    except FileNotFoundError:
        print(f"CSV file not found: {csv_file}")
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {str(e)}")
    return []

def process_json_file(json_file, valid_ids):
    """Processes a single JSON file, cleaning data and extracting necessary fields."""
    try:
        # Log the path for debugging
        print(f"Processing file: {json_file}")
        
        # Open the JSON file
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Extract and clean fields from the JSON
        doc_id = data.get("docId", "").strip()
        if doc_id in valid_ids:
            metadata = data.get('metadata', {})
            
            # Clean the metadata fields
            title = clean_text(metadata.get('title', ''))
            authors = metadata.get('authors', [])
            
            # Join first and last names of authors
            authors_cleaned = [
                f"{author['first']} {author['last']}".strip() for author in authors
            ]
            
            # Handle abstract which can be a string or list
            abstract_data = data.get('abstract', [])
            if isinstance(abstract_data, list):
                # If it's a list of sentences, clean each sentence
                abstract = " ".join([clean_text(sentence.get('sentence', '')) for sentence in abstract_data])
            elif isinstance(abstract_data, str):
                # If it's a single string, clean it directly
                abstract = clean_text(abstract_data)
            else:
                abstract = ""  # If no valid abstract data is found

            bib_entries = data.get('bib_entries', {})
            
            # Return cleaned and relevant data
            return {
                'docId': doc_id,
                'title': title,
                'authors': ", ".join(authors_cleaned),  # Combine authors into a single string
                'abstract': abstract,
                'bib_entries': bib_entries,
            }
    except FileNotFoundError:
        print(f"File not found: {json_file}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON in file: {json_file}")
    except Exception as e:
        print(f"An error occurred while processing file {json_file}: {str(e)}")
    
    # Return None if there was an error
    return None

def process_json_folder(folder_path, valid_ids):
    """Iterates through all JSON files in the folder and processes each one."""
    cleaned_data = []
    for json_file in os.listdir(folder_path):
        if json_file.endswith('.json'):
            json_path = os.path.join(folder_path, json_file)
            result = process_json_file(json_path, valid_ids)
            if result:
                cleaned_data.append(result)
    return cleaned_data

def save_to_csv(data, output_csv_file):
    """Saves the cleaned data to a CSV file, converting bib_entries to a string."""
    if data:
        # Add 'bib_entries' to the fieldnames list
        fieldnames = ['docId', 'title', 'authors', 'abstract', 'bib_entries']  # Add other fields as needed

        # Convert 'bib_entries' (which is a dictionary) to a string representation
        for item in data:
            if 'bib_entries' in item:
                item['bib_entries'] = json.dumps(item['bib_entries'])  # Convert dict to JSON string for CSV

        with open(output_csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        print(f"Cleaned data has been saved to {output_csv_file}.")

def main():
    # Load the CSV file with IDs
    csv_file = 'os-ccby-40k-ids.csv'
    valid_ids = load_csv(csv_file)
    
    if not valid_ids:
        print("No valid IDs were loaded from the CSV file. Exiting.")
        return
    
    # Process JSON files in the folder
    json_folder = 'train_data'  # Replace with your actual folder name
    if not os.path.isdir(json_folder):
        print(f"The folder {json_folder} does not exist. Please provide a valid folder path.")
        return
    
    cleaned_data = process_json_folder(json_folder, valid_ids)
    
    if cleaned_data:
        # Output the cleaned data to a JSON file
        output_json_file = 'cleaned_data.json'
        with open(output_json_file, 'w', encoding='utf-8') as outfile:
            json.dump(cleaned_data, outfile, ensure_ascii=False, indent=4)
        print(f"Cleaned data has been saved to {output_json_file}.")
        
        # Output the cleaned data to a CSV file
        output_csv_file = 'cleaned_data.csv'
        save_to_csv(cleaned_data, output_csv_file)
    else:
        print("No cleaned data was generated.")

if __name__ == "__main__":
    main()
