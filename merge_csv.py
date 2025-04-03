import pandas as pd


def map_items(item_str, item_df):
    """Maps a string of item numbers (separated by '_') to their descriptions, scales, and phrasing."""
    item_numbers = item_str.split('_')  # Split multi-item nodes
    filtered_df = item_df[item_df['item_number'].astype(str).isin(item_numbers)]
    
    # Concatenating values using ';' as separator
    scale = ';'.join(filtered_df['scale'].astype(str))
    description = ';'.join(filtered_df['description'].astype(str))
    positively_phrased = ';'.join(filtered_df['is_positively_phrased'].astype(str))
    
    return scale, description, positively_phrased


if __name__ == '__main__':
    # File paths
    link_file_path = "data/edi3/pale_predictions/pale-h1_an_bn.csv"
    items_file_path = "data/edi3/edi3_items_subscales_copy.csv"
    output_file_path = "data/edi3/pale_predictions/extended_pale_h1_an_bn.csv"

    df_links = pd.read_csv(link_file_path)
    df_items = pd.read_csv(items_file_path)

    # Apply mapping function to source and target nodes
    df_links[['source_scale', 'source_description', 'source_positively_phrased']] = df_links['source_node'].apply(
        lambda x: pd.Series(map_items(x, df_items))
    )

    df_links[['target_scale', 'target_description', 'target_positively_phrased']] = df_links['target_node'].apply(
        lambda x: pd.Series(map_items(x, df_items))
    )

    # Reorder columns
    df_final = df_links[[
        'source_node', 'target_node', 'num_predictions', 'is_seed',
        'source_scale', 'target_scale', 'source_description', 'target_description',
        'source_positively_phrased', 'target_positively_phrased'
    ]]

    # Save merged file
    df_final.to_csv(output_file_path, index=False)

    print(f"Processed file saved as: {output_file_path}")
