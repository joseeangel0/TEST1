
import requests
import json
import os
from datetime import datetime

# The API endpoint for people
API_URL = "https://swapi.dev/api/people/"

# Directory to save the raw data
OUTPUT_DIR = "local_output/raw"

def fetch_all_people_data():
    """
    Fetches all people data from the SWAPI API, handling pagination.
    """
    all_people = []
    url = API_URL
    print("Starting data extraction from SWAPI...")
    
    while url:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()
            all_people.extend(data["results"])
            url = data["next"]  # Get the URL for the next page
            if url:
                print(f"Fetching next page: {url}")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
            
    print(f"Extraction complete. Total characters fetched: {len(all_people)}")
    return all_people

def save_data_to_json(data):
    """
    Saves the provided data to a JSON file in the output directory.
    The filename includes a timestamp.
    """
    if data is None:
        print("No data to save.")
        return

    # Ensure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Create a timestamp for the filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"people_{timestamp}.json"
    file_path = os.path.join(OUTPUT_DIR, file_name)
    
    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Data successfully saved to: {file_path}")
    except IOError as e:
        print(f"Error saving data to file: {e}")

if __name__ == "__main__":
    people_data = fetch_all_people_data()
    save_data_to_json(people_data)
