import os
import pandas as pd

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

def calculate_consecutive_differences(counts):
    """Calculate differences between consecutive days."""
    return [counts[i+1] - counts[i] for i in range(len(counts)-1)]

def create_difference_summary(total_counts, married_counts, single_counts, 
                             with_children_counts, without_children_counts, day_labels):
    """Create a summary table of consecutive differences."""
    # Calculate differences for consecutive days
    total_diffs = calculate_consecutive_differences(total_counts)
    married_diffs = calculate_consecutive_differences(married_counts)
    single_diffs = calculate_consecutive_differences(single_counts)
    with_children_diffs = calculate_consecutive_differences(with_children_counts)
    without_children_diffs = calculate_consecutive_differences(without_children_counts)
    
    # Create row labels for consecutive differences (e.g., 'day2-day1')
    diff_labels = [f"{day_labels[i+1]}-{day_labels[i]}" for i in range(len(day_labels)-1)]
    
    # Create DataFrame
    data = {
        'total_diff': total_diffs,
        'married_diff': married_diffs,
        'single_diff': single_diffs,
        'with_children_diff': with_children_diffs,
        'without_children_diff': without_children_diffs
    }
    df = pd.DataFrame(data, index=diff_labels)
    return df

def save_difference_summary(df, output_path):
    """Save the difference summary as a CSV file."""
    df.to_csv(output_path)
    return df

def main(folder_path, output_file='consecutive_difference_summary.csv'):
    """Main function to process CSV files and generate consecutive difference summary."""
    # Get all CSV files
    csv_files = get_csv_files(folder_path)
    if not csv_files:
        print("No CSV files found in the specified folder.")
        return
    
    # Read participant counts for all categories
    (total_counts, married_counts, single_counts, 
     with_children_counts, without_children_counts, day_labels) = read_event_data(csv_files)
    
    if not total_counts or len(total_counts) < 2:
        print("Insufficient valid data (need at least 2 days) to calculate differences.")
        return
    
    # Create difference summary
    df = create_difference_summary(
        total_counts, married_counts, single_counts, 
        with_children_counts, without_children_counts, day_labels
    )
    
    # Save and display the summary
    df = save_difference_summary(df, output_file)
    print("\nConsecutive Difference Summary:")
    print(df)

if __name__ == "__main__":
    # Specify the folder containing the CSV files
    folder_path = input("Enter the folder path containing the CSV files: ")
    main(folder_path)
