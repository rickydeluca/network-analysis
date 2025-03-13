import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

# Input and output dirs.
input_dir = "data/edi3/pale_predictions"   
output_dir = "plots/pale_predictions/barplot/"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

csv_files = glob.glob(os.path.join(input_dir, '*.csv'))

# Set the tick frequency and font.
tick_frequency = 5
tick_font_size = 6

for file in csv_files:
    df = pd.read_csv(file)
    
    # Extract the numerator from each 'num_predictions' entry.
    numerators = df['num_predictions'].apply(lambda x: int(str(x).split('/')[0]))
    
    # Plot.
    plt.figure(figsize=(10, 6))

    plt.bar(range(len(numerators)), numerators, color='skyblue')
    
    plt.xlabel('Row Number')
    plt.ylabel('Number of predictions')
    plt.title(f"Number of PALE predictions on 100 experiments | {os.path.basename(file)}")
    
    # Set x-axis tick labels at intervals defined by tick_frequency with modified font for the tick numbers.
    tick_indices = list(range(0, len(numerators), tick_frequency))
    plt.xticks(tick_indices, tick_indices, rotation=45, ha='right', fontsize=tick_font_size)
    
    plt.tight_layout()
    
    # Save plot.
    file_basename = os.path.splitext(os.path.basename(file))[0]
    output_file = os.path.join(output_dir, f"{file_basename}_barplot.png")
    plt.savefig(output_file)
    plt.close()
