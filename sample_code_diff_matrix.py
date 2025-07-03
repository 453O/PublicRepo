import os
import pandas as pd
import numpy as np
from itertools import combinations

# Specify the folder path containing CSV files
folder_path = "--"  # Replace with your folder path

# Function to read all CSV files in the folder
def read_csv_files(folder_path):
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    dataframes = []
    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path)
        # Standardize column names (assuming columns might vary slightly)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        # Ensure required columns exist
        required_columns = ['name', 'marital_status', 'have_children']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"File {file} missing required columns: {required_columns}")
        # Add a column to indicate the day (derived from file name or order)
        df['day'] = file.replace('.csv', '')
        dataframes.append(df)
    return dataframes, csv_files

# Function to create a unique identifier for each attendee
def create_attendee_id(row):
    return f"{row['name']}_{row['marital_status']}_{row['have_children']}"

# Function to compute participant counts and differences
def compute_difference_matrix(dataframes, csv_files):
    # Combine all dataframes and create a unique attendee ID
    combined_df = pd.concat(dataframes, ignore_index=True)
    combined_df['attendee_id'] = combined_df.apply(create_attendee_id, axis=1)
    
    # Pivot table to get participant counts per day
    pivot = combined_df.pivot_table(
        index='attendee_id',
        columns='day',
        aggfunc='size',
        fill_value=0
    )
    
    # Ensure all days are included in the pivot table
    pivot = pivot.reindex(columns=[f.replace('.csv', '') for f in csv_files], fill_value=0)
    
    # Calculate total participants per day
    total_participants = pivot.sum()
    
    # Initialize difference matrix
    days = pivot.columns
    n_days = len(days)
    diff_matrix = pd.DataFrame(0, index=days, columns=days)
    
    # Compute absolute differences in participant counts between each pair of days
    for day1, day2 in combinations(days, 2):
        diff = abs(total_participants[day1] - total_participants[day2])
        diff_matrix.loc[day1, day2] = diff
        diff_matrix.loc[day2, day1] = diff
    
    return diff_matrix, total_participants

# Main execution
def main():
    try:
        # Read CSV files
        dataframes, csv_files = read_csv_files(folder_path)
        if len(dataframes) == 0:
            raise ValueError("No CSV files found in the specified folder.")
        
        # Compute difference matrix and total participants
        diff_matrix, total_participants = compute_difference_matrix(dataframes, csv_files)
        
        # Print results
        print("\nTotal Participants per Day:")
        print(total_participants)
        print("\nDifference Matrix (Absolute Differences in Participant Counts):")
        print(diff_matrix)
        
        # Optionally, save the difference matrix to a CSV file
        output_path = os.path.join(folder_path, 'difference_matrix.csv')
        diff_matrix.to_csv(output_path)
        print(f"\nDifference matrix saved to {output_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
