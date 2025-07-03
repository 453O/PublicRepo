import os
import pandas as pd
import numpy as np

def get_csv_files(folder_path):
    """Retrieve all CSV files from the specified folder, sorted by filename."""
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    # Attempt to sort files chronologically assuming filenames contain numbers
    try:
        csv_files.sort(key=lambda x: int(''.join(filter(str.isdigit, x))) if any(c.isdigit() for c in x) else x)
    except:
        csv_files.sort()  # Fallback to alphabetical sorting if numerical sorting fails
    return [os.path.join(folder_path, f) for f in csv_files]

def read_event_data(file_paths):
    """Read participant counts for all categories from CSV files."""
    total_counts = []
    married_counts = []
    single_counts = []
    with_children_counts = []
    without_children_counts = []
    day_labels = []
    
    for file_path in file_paths:
        try:
            df = pd.read_csv(file_path)
            # Count participants for each category (case-insensitive)
            total_count = len(df)
            married_count = len(df[df['marital_status'].str.lower() == 'married'])
            single_count = len(df[df['marital_status'].str.lower() == 'single'])
            with_children_count = len(df[df['has_children'].str.lower() == 'yes'])
            without_children_count = len(df[df['has_children'].str.lower() == 'no'])
            
            total_counts.append(total_count)
            married_counts.append(married_count)
            single_counts.append(single_count)
            with_children_counts.append(with_children_count)
            without_children_counts.append(without_children_count)
            
            # Extract day label from filename
            day_label = os.path.basename(file_path).replace('.csv', '')
            day_labels.append(day_label)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue
    
    return (total_counts, married_counts, single_counts, 
            with_children_counts, without_children_counts, day_labels)

def create_difference_matrix(counts, labels):
    """Create a difference matrix for given counts between days."""
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

def main(folder_path):
    """Main function to process CSV files and generate all difference matrices."""
    # Get all CSV files
    csv_files = get_csv_files(folder_path)
    if not csv_files:
        print("No CSV files found in the specified folder.")
        return
    
    # Read participant counts for all categories
    (total_counts, married_counts, single_counts, 
     with_children_counts, without_children_counts, day_labels) = read_event_data(csv_files)
    
    if not total_counts:
        print("No valid data processed from CSV files.")
        return
    
    # Create and save difference matrices
    matrices = [
        (total_counts, 'total_difference_matrix.csv', "Total Participants"),
        (married_counts, 'married_difference_matrix.csv', "Married Participants"),
        (single_counts, 'single_difference_matrix.csv', "Single Participants"),
        (with_children_counts, 'with_children_difference_matrix.csv', "Participants with Children"),
        (without_children_counts, 'without_children_difference_matrix.csv', "Participants without Children")
    ]
    
    for counts, output_file, title in matrices:
        diff_matrix, labels = create_difference_matrix(counts, day_labels)
        df = save_difference_matrix(diff_matrix, labels, output_file)
        print(f"\n{title} Difference Matrix:")
        print(df)

if __name__ == "__main__":
    # Specify the folder containing the CSV files
    folder_path = input("Enter the folder path containing the CSV files: ")
    main(folder_path)
