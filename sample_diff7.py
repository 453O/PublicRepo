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
        csv_files.sort()  # Fallback to alphabetical sorting
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

def create_formatted_difference_matrix(total_counts, married_counts, single_counts, 
                                      with_children_counts, without_children_counts, day_labels):
    """Create a difference matrix with tuple-formatted strings in each cell."""
    n = len(day_labels)
    diff_matrix = np.empty((n, n), dtype=object)  # Use object type to store strings
    
    for i in range(n):
        for j in range(n):
            total_diff = total_counts[j] - total_counts[i]
            married_diff = married_counts[j] - married_counts[i]
            single_diff = single_counts[j] - single_counts[i]
            with_children_diff = with_children_counts[j] - with_children_counts[i]
            without_children_diff = without_children_counts[j] - without_children_counts[i]
            # Format the string as a tuple for the cell
            diff_matrix[i, j] = (
                f"(total_diff:{total_diff}, "
                f"married_diff:{married_diff}, "
                f"single_diff:{single_diff}, "
                f"with_children_diff:{with_children_diff}, "
                f"without_children_diff:{without_children_diff})"
            )
    
    # Create DataFrame
    df = pd.DataFrame(diff_matrix, index=day_labels, columns=day_labels)
    return df

def save_difference_matrix(df, output_path):
    """Save the difference matrix as a CSV file."""
    df.to_csv(output_path)
    return df

def main(folder_path, output_file='tuple_formatted_difference_matrix.csv'):
    """Main function to process CSV files and generate tuple-formatted difference matrix."""
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
    
    # Create formatted difference matrix
    df = create_formatted_difference_matrix(
        total_counts, married_counts, single_counts, 
        with_children_counts, without_children_counts, day_labels
    )
    
    # Save and display the matrix
    df = save_difference_matrix(df, output_file)
    print("\nTuple-Formatted Difference Matrix:")
    print(df)

if __name__ == "__main__":
    # Specify the folder containing the CSV files
    folder_path = input("Enter the folder path containing the CSV files: ")
    main(folder_path)
