
import json
import boto3
import requests
from datetime import datetime
import os

# --- Configuration ---
S3_BUCKET_NAME = "instructions-67f86d4f"
S3_RAW_PREFIX = "raw/"
API_URL = "https://swapi.dev/api/people/"

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
            response.raise_for_status()
            data = response.json()
            all_people.extend(data["results"])
            url = data.get("next") # Use .get for safer access
            if url:
                print(f"Fetching next page: {url}")
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Could not fetch data: {e}")
            raise
            
    print(f"Extraction complete. Total characters fetched: {len(all_people)}")
    return all_people

def lambda_handler(event, context):
    """
    The main handler for the AWS Lambda function.
    Fetches data and uploads it to S3.
    """
    s3_client = boto3.client("s3")
    
    try:
        # 1. Fetch data from the API
        people_data = fetch_all_people_data()
        
        if not people_data:
            print("No data fetched, exiting.")
            return {'statusCode': 500, 'body': json.dumps('Failed to fetch data from API')}

        # 2. Prepare the file for S3
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"people_{timestamp}.json"
        s3_key = os.path.join(S3_RAW_PREFIX, file_name)
        
        # 3. Upload the data to S3
        print(f"Uploading data to S3 bucket '{S3_BUCKET_NAME}' at key '{s3_key}'...")
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=json.dumps(people_data, indent=4),
            ContentType='application/json'
        )
        
        print("Upload successful.")
        return {
            'statusCode': 200,
            'body': json.dumps(f'Successfully processed and uploaded {s3_key}')
        }

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # It's good practice to log the full error for debugging
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps(f'An error occurred: {str(e)}')
        }
