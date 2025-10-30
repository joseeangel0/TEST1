
import pandas as pd
import numpy as np
import os
import glob
import json

RAW_DATA_DIR = "local_output/raw"
PROCESSED_DATA_DIR = "local_output/processed"

def find_latest_raw_file():
    """Finds the most recently created JSON file in the raw data directory."""
    list_of_files = glob.glob(os.path.join(RAW_DATA_DIR, '*.json'))
    if not list_of_files:
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

def transform_data(file_path):
    """Applies all the transformations as described in the instructions."""
    print(f"Starting transformation for file: {file_path}")

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error reading or parsing JSON file: {e}")
        return None

    # 1. Select required columns
    required_columns = ['name', 'height', 'mass', 'hair_color', 'skin_color', 'eye_color', 'birth_year', 'gender']
    df = df[required_columns]
    print(f"Initial row count: {len(df)}")

    # Replace 'unknown' and 'n/a' with NaN for easier processing
    df.replace(['unknown', 'n/a'], np.nan, inplace=True)

    # 2. Create 'normalized_birth_year'
    def normalize_birth_year(by):
        if pd.isna(by) or 'BBY' not in by:
            return np.nan
        try:
            year = float(by.replace('BBY', ''))
            return 2000 - year
        except (ValueError, TypeError):
            return np.nan
    df['normalized_birth_year'] = df['birth_year'].apply(normalize_birth_year)

    # 3. Create 'mass_lb'
    def convert_mass_to_lb(mass):
        if pd.isna(mass):
            return np.nan
        try:
            mass_kg = float(str(mass).replace(',', ''))
            return mass_kg * 2.20462
        except (ValueError, TypeError):
            return np.nan
    df['mass_lb'] = df['mass'].apply(convert_mass_to_lb)
    
    # Convert original mass to numeric for filtering, coercing errors
    df['mass'] = pd.to_numeric(df['mass'].astype(str).str.replace(',', ''), errors='coerce')

    # 4. Create 'gender_id'
    def assign_gender_id(gender):
        if pd.isna(gender):
            return 'N'
        if gender.lower() == 'male':
            return 'M'
        if gender.lower() == 'female':
            return 'F'
        return 'N'
    df['gender_id'] = df['gender'].apply(assign_gender_id)

    # 5. Filter out rows where mass > 1000
    initial_rows = len(df)
    df = df[df['mass'] <= 1000]
    print(f"Rows removed due to mass > 1000kg: {initial_rows - len(df)}")

    # 6. Filter rows with 3 or more empty fields
    initial_rows = len(df)
    df = df.dropna(thresh=df.shape[1] - 2) # Keep rows with at least (total_columns - 2) non-NA values
    print(f"Rows removed due to 3 or more missing values: {initial_rows - len(df)}")

    print(f"Final row count after transformations: {len(df)}")
    return df

def save_to_csv(df, original_filename):
    """Saves the transformed DataFrame to a CSV file."""
    if df is None:
        print("No data to save.")
        return

    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    base_filename = os.path.basename(original_filename)
    csv_filename = os.path.splitext(base_filename)[0] + '.csv'
    output_path = os.path.join(PROCESSED_DATA_DIR, csv_filename)
    
    try:
        df.to_csv(output_path, index=False)
        print(f"Transformed data successfully saved to: {output_path}")
    except IOError as e:
        print(f"Error saving CSV file: {e}")

if __name__ == "__main__":
    latest_file = find_latest_raw_file()
    if latest_file:
        transformed_df = transform_data(latest_file)
        save_to_csv(transformed_df, latest_file)
    else:
        print("No raw data files found. Please run the extractor script first.")
