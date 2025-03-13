import os
import csv
import glob

# Input and output directories.
input_directory = "data/edi3/pale_predictions"
output_directory = "data/edi3/updated_pale_predictions"

if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Define header.
header = ['source_node', 'target_node', 'num_predictions', 'is_seed']

# Process files.
for filepath in glob.glob(os.path.join(input_directory, "*.csv")):
    with open(filepath, mode='r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)
    
    # Insert header if not present.
    if rows and rows[0] != header:
        rows.insert(0, header)
    
    # Start processing from the second row.
    for i in range(1, len(rows)):
        if len(rows[i]) >= 4:
            # Strip extra whitespaces from the last columns.
            cell_value = rows[i][-1].strip().lower()
            if cell_value == "is_seed":
                rows[i][-1] = "True"
            elif cell_value == "":
                rows[i][-1] = "False"
            else:
                pass
    
    # Write updated file.
    output_path = os.path.join(output_directory, os.path.basename(filepath))
    with open(output_path, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)

print("CSV file processing complete. Modified files are located in:", output_directory)
