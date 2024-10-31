import csv
import json
import re

# Load the CSV file and parse each row
def load_csv(file_path):
    characters = []
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')  # Specify semicolon as delimiter
        for row in reader:
            character = {
                "Name": [name.strip().lower() for name in row['Name'].split('/')],  # Split multiple names by '/' and lowercase
                "Sex": row['Sex'].strip().lower() if row['Sex'] else "unknown",  # Default to "unknown" if empty
                "Gen": row['Gen'].strip().lower(),
                "Dates": row['Dates'].strip().lower(),
                "Clan": row['Clan'].strip().lower(),
                "Progeny": re.split(r'\s{2,}|\n', row['Progeny'].strip().lower()) if row['Progeny'] else [],  # Split by double spaces or newlines
                "References": [ref.strip().lower() for ref in row['References'].split() if ref]  # Split by whitespace for each reference
            }
            characters.append(character)
    return characters

# Helper function to match names
def find_character_id(name, alias_map):
    name_parts = name.split()
    num_parts = len(name_parts)

    # Attempt matching by adding one word at a time to find a unique match
    for i in range(num_parts):
        for j in range(i + 1, num_parts + 1):
            search_name = ' '.join(name_parts[i:j])  # Form the search term with increasing specificity
            matches = [alias_map[n] for n in alias_map if n == search_name]
            
            # If we find exactly one match, return it
            if len(matches) == 1:
                return matches[0]
    # No unique match found
    return None

# Generate elements (nodes) and connections (links) for Kumu
def generate_kumu_json(characters):
    elements = []
    connections = []
    name_to_id = {}  # Dictionary to store ID mapping for each name
    alias_map = {}   # Map all aliases to the main ID

    # Generate elements (nodes)
    for idx, character in enumerate(characters):
        # Use the first name as the main label, but keep others as aliases
        main_name = character['Name'][0]
        aliases = character['Name'][1:]

        element = {
            "id": idx,
            "label": main_name,
            "data": {
                "Aliases": aliases,  # Store alternative names
                "Sex": character['Sex'],
                "Generation": character['Gen'],
                "Dates": character['Dates'],
                "Clan": character['Clan'],
                "References": character['References']
            }
        }
        elements.append(element)
        name_to_id[main_name] = idx  # Map main name to element ID

        # Map all aliases to the main ID
        alias_map[main_name] = idx
        for alias in aliases:
            alias_map[alias] = idx

    # Generate connections (links)
    for character in characters:
        parent_id = alias_map.get(character['Name'][0])  # Resolve main name to ID using alias map

        for progeny_name in character['Progeny']:
            # Attempt to find the child ID by progressively adding more words
            child_id = find_character_id(progeny_name, alias_map)

            if child_id is not None:  # Ensure child exists in data
                connection = {
                    "source": parent_id,
                    "target": child_id,
                    "type": "sire-childe"  # Relationship type for clarity
                }
                connections.append(connection)

    # Combine elements and connections for Kumu JSON structure
    kumu_data = {
        "elements": elements,
        "connections": connections
    }
    
    return kumu_data

# Main function to load CSV, convert to JSON, and save output
def main(csv_path, output_json_path):
    characters = load_csv(csv_path)
    kumu_data = generate_kumu_json(characters)
    
    # Save JSON data to output file
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(kumu_data, json_file, indent=4)
    print(f"Kumu JSON data saved to {output_json_path}")

# Specify the paths for the input CSV and output JSON file
csv_path = 'genealogy.csv'  # Replace with the actual CSV file path
output_json_path = 'kumu_data.json'

# Run the script
main(csv_path, output_json_path)
