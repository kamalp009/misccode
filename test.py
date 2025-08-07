import pandas as pd
from collections import OrderedDict
import re

def combine_and_deduplicate_descriptions(df):
    """
    Combine short descriptions for same KEDB numbers and create unique patterns
    """
    result_data = {
        'KEDB': [],
        'short description': [],
        'unique_pattern': []
    }
    
    # Group by KEDB number
    grouped = df.groupby('KEDB')
    
    for kedb, group in grouped:
        # Get all descriptions for this KEDB
        descriptions = group['short description'].tolist()
        
        # Combine all descriptions with ' - ' separator
        combined_description = ' - '.join(descriptions)
        
        # Create unique pattern by removing duplicates while preserving order
        all_words = []
        for desc in descriptions:
            # Split description into words and clean them
            words = re.findall(r'\b\w+\b', desc.lower())
            all_words.extend(words)
        
        # Remove duplicates while preserving order
        unique_words = list(OrderedDict.fromkeys(all_words))
        unique_pattern = ' '.join(unique_words)
        
        # Add to result
        result_data['KEDB'].append(kedb)
        result_data['short description'].append(combined_description)
        result_data['unique_pattern'].append(unique_pattern)
    
    return pd.DataFrame(result_data)

def process_excel_file(input_file_path, output_file_path):
    """
    Process Excel file and create new file with combined data
    """
    try:
        # Read the Excel file
        df = pd.read_excel(input_file_path)
        
        # Ensure column names are correct (handle different naming conventions)
        if 'short description' in df.columns:
            pass
        elif 'Short_description' in df.columns:
            df.rename(columns={'Short_description': 'short description'}, inplace=True)
        elif 'Short Description' in df.columns:
            df.rename(columns={'Short Description': 'short description'}, inplace=True)
        else:
            raise ValueError("Could not find short description column")
        
        # Process the data
        result_df = combine_and_deduplicate_descriptions(df)
        
        # Save to new Excel file
        result_df.to_excel(output_file_path, index=False)
        
        print(f"Processing completed successfully!")
        print(f"Input file: {input_file_path}")
        print(f"Output file: {output_file_path}")
        print(f"Original rows: {len(df)}")
        print(f"Processed rows: {len(result_df)}")
        
        return result_df
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return None

# Example usage with sample data
def create_sample_and_test():
    """
    Create sample data and test the functionality
    """
    # Sample data as provided in the question
    data = {
        'KEDB': ['K001', 'K001', 'K001', 'K002', 'K002', 'K003'],
        'short description': [
            'system error network failure',
            'network failure database issue',
            'system error connection timeout',
            'login problem user access',
            'user access denied login problem',
            'server maintenance scheduled downtime'
        ]
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save sample data to Excel
    sample_file = 'sample_input.xlsx'
    df.to_excel(sample_file, index=False)
    print(f"Sample input file created: {sample_file}")
    
    # Process the sample data
    output_file = 'processed_output.xlsx'
    result_df = process_excel_file(sample_file, output_file)
    
    if result_df is not None:
        print("\nProcessed Data:")
        print(result_df.to_string(index=False))
        
        print("\nDetailed Results:")
        for index, row in result_df.iterrows():
            print(f"\nKEDB: {row['KEDB']}")
            print(f"Combined Description: {row['short description']}")
            print(f"Unique Pattern: {row['unique_pattern']}")

# Alternative function if you want to work directly with data in memory
def process_dataframe_directly():
    """
    Process data directly without file I/O
    """
    # Sample data
    data = {
        'KEDB': ['K001', 'K001', 'K001', 'K002', 'K002', 'K003'],
        'short description': [
            'system error network failure',
            'network failure database issue',
            'system error connection timeout',
            'login problem user access',
            'user access denied login problem',
            'server maintenance scheduled downtime'
        ]
    }
    
    df = pd.DataFrame(data)
    result_df = combine_and_deduplicate_descriptions(df)
    
    # Save to Excel
    output_file = 'direct_processed_output.xlsx'
    result_df.to_excel(output_file, index=False)
    
    return result_df

# Main execution
if __name__ == "__main__":
    # Option 1: Create and test with sample data
    print("=== Testing with Sample Data ===")
    create_sample_and_test()
    
    print("\n" + "="*50)
    
    # Option 2: Process your actual Excel file
    # Uncomment and modify the file paths below to use with your actual files
    """
    print("=== Processing Your Excel File ===")
    input_file = "your_input_file.xlsx"  # Replace with your input file path
    output_file = "your_output_file.xlsx"  # Replace with desired output file path
    
    result = process_excel_file(input_file, output_file)
    """
    
    print("\n=== Direct DataFrame Processing ===")
    result_direct = process_dataframe_directly()
    print("Direct processing completed!")
