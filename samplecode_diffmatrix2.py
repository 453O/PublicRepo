import os
import pandas as pd
import numpy as np
from datetime import datetime

def get_csv_files(folder_path):
    """Retrieve all CSV files from the specified folder, sorted by filename."""
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    # Attempt to sort files chronologically assuming filenames contain dates or numbers
    try:
        csv_files.sort(key=lambda x: int(''.join(filter(str.isdigit, x))) if any(c.isdigit() for c in x) else x)
    except:
        csv_files.sort()  # Fallback to alphabetical sorting if numerical sorting fails
    return [os.path.join(folder_path, f) for f in csv_files]

def read_event_data(file_paths):
    """Read participant counts from all CSV files."""
    participant_counts = []
    day_labels = []
    
    for file_path in file_paths:
        try:
            df = pd.read_csv(file_path)
            # Count total participants per file
            count = len(df)
            participant_counts.append(count)
            # Extract day label from filename (e.g., 'day1' from 'event_day1.csv')
            day_label = os.path.basename(file_path).replace('.csv', '')
            day_labels.append(day_label)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue
    
    return participant_counts, day_labels

def create_difference_matrix(counts, labels):
    """Create a difference matrix of participant counts between days."""
    n = len(counts)
    diff_matrix = np.zeros((n, n), dtype=int)
    
    for i in range(n):
        for j in range(n):
            diff_matrix[i, j] = counts[j] - counts[i]
    
    return diff_matrix, labels

def save_difference_matrix(matrix, labels, output_path):
    """Save the difference matrix as a CSV file."""
    df = pd.DataFrame(matrix, index=labels, columns=labels)
    df.to_csv(output_path)
    return df

def main(folder_path, output_file='difference_matrix.csv'):
    """Main function to process CSV files and generate difference matrix."""
    # Get all CSV files
    csv_files = get_csv_files(folder_path)
    if not csv_files:
        print("No CSV files found in the specified folder.")
        return
    
    # Read participant counts
    participant_counts, day_labels = read_event_data(csv_files)
    if not participant_counts:
        print("No valid data processed from CSV files.")
        return
    
    # Create difference matrix
    diff_matrix, labels = create_difference_matrix(participant_counts, day_labels)
    
    # Save and display the matrix
    df = save_difference_matrix(diff_matrix, labels, output_file)
    print("Difference Matrix:")
    print(df)

if __name__ == "__main__":
    # Specify the folder containing the CSV files
    folder_path = input("Enter the folder path containing the CSV files: ")
    main(folder_path)
