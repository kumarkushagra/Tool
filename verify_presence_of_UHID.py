import pandas as pd
import os

def check_file_presence_across_system(csv_file_path):
    # Read the CSV file
    df = pd.read_csv(csv_file_path)
    
    # Extract UHID names from the 'Patient ID(UHID)' column
    uhid_names = df['Patient ID(UHID)'].tolist()
    
    # Initialize lists to store results
    found_files = []
    not_found_files = []
    
    # Iterate over each UHID name
    for uhid in uhid_names:
        file_name = f"{uhid}.txt"  # Adjust file extension or naming convention as needed
        
        file_found = False
        
        # Traverse the entire file system using os.walk()
        for root, dirs, files in os.walk('/'):  # Start from the root directory '/'
            if file_name in files:
                file_path = os.path.join(root, file_name)
                found_files.append((uhid, file_path))
                file_found = True
                break
        
        if not file_found:
            not_found_files.append(uhid)
    
    # Update the DataFrame with the results
    for uhid, path in found_files:
        # Find the index of the row with the corresponding UHID and update the 'Path' column
        df.loc[df['Patient ID(UHID)'] == uhid, 'Path'] = path
    
    # Save the updated DataFrame back to the CSV file
    df.to_csv(csv_file_path, index=False)
    
    # Print summary
    print(f"Found {len(found_files)} files.")
    print(f"Files not found for UHIDs: {', '.join(not_found_files)}")

# Example usage:
csv_file_path = '/home/ubuntu/kushagr/Tag_Team_6/check_UHIDs_in_dataset/CSV_files/uncommon.csv'
check_file_presence_across_system(csv_file_path)
