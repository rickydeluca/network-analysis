import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import re

def process_directory(directory, output_directory, include_seeds):
    """Processes all CSV files in a directory and generates distribution plots."""
    if not os.path.isdir(directory):
        print(f"Error: The directory '{directory}' does not exist.")
        return
    
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    for file_name in os.listdir(directory):
        if file_name.endswith(".csv"):
            file_path = os.path.join(directory, file_name)
            print(f"Processing: {file_path}")
            plot_distribution(file_path, output_directory, include_seeds)

def plot_distribution(file_path, output_directory, include_seeds=True):
    df = pd.read_csv(file_path)

    if not include_seeds:
        # Exclude seed pairs
        df = df[df[df.columns[3]] != 'is_seed']
    
    # Get number of alignment pairs
    third_column = df.columns[2]
    
    # Extract only the first part of '<number>/100'
    df[third_column] = df[third_column].astype(str).str.extract(r'(\d+)')[0].astype(float)
    
    # Plot
    plt.figure(figsize=(10, 6))
    sns.histplot(df[third_column], kde=True)
    plt.xlabel("Times of predictions")
    plt.ylabel("Frequency")
    plt.title(f"Distribution of {third_column}" + (" (excluding seed nodes)" if not include_seeds else ""))
    
    # Adjust x-axis to prevent overlap
    plt.xticks(rotation=45)
    
    # Save plot
    output_file = os.path.join(output_directory, os.path.basename(file_path).replace(".csv", ".png"))
    plt.savefig(output_file)
    plt.close()
    print(f"Plot saved: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot distributions from CSV files in a directory.")
    parser.add_argument("directory", type=str, help="Path to the directory containing CSV files.")
    parser.add_argument("output_directory", type=str, help="Path to the directory where plots will be saved.")
    parser.add_argument("--exclude-seeds", action="store_true", help="Exclude seed nodes from the analysis.")

    args = parser.parse_args()
    
    process_directory(args.directory, args.output_directory, not args.exclude_seeds)
