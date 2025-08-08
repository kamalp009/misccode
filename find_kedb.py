import pandas as pd

def find_kedb_data(excel_file, kedb_number):
    """
    Find a specific KEDB number in ServicenowID column and return corresponding data
    
    Parameters:
    excel_file (str): Path to the Excel file
    kedb_number (str): The KEDB number to search for
    
    Returns:
    dict: Dictionary containing the found data or None if not found
    """
    try:
        # Read the Excel file
        df = pd.read_excel(excel_file)
        
        # Check if required columns exist
        required_columns = ['short_description', 'Description', 'ServicenowID']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"Error: Missing columns in Excel file: {missing_columns}")
            return None
        
        # Search for the KEDB number in ServicenowID column
        # Using case-insensitive search and converting to string for comparison
        mask = df['ServicenowID'].astype(str).str.contains(str(kedb_number), case=False, na=False)
        matching_rows = df[mask]
        
        if matching_rows.empty:
            print(f"KEDB number '{kedb_number}' not found in ServicenowID column")
            return None
        
        # If multiple matches found, take the first one and notify user
        if len(matching_rows) > 1:
            print(f"Warning: Multiple matches found for '{kedb_number}'. Returning the first match.")
        
        # Extract the data from the first matching row
        row = matching_rows.iloc[0]
        result = {
            'ServicenowID': row['ServicenowID'],
            'short_description': row['short_description'],
            'Description': row['Description']
        }
        
        return result
        
    except FileNotFoundError:
        print(f"Error: File '{excel_file}' not found")
        return None
    except Exception as e:
        print(f"Error reading Excel file: {str(e)}")
        return None

def main():
    # Configuration
    excel_file = "kedb_data.xlsx"
    
    # Get KEDB number from user input
    kedb_number = input("Enter the KEDB number to search for: ")
    
    # Search for the KEDB data
    result = find_kedb_data(excel_file, kedb_number)
    
    if result:
        print("\n" + "="*50)
        print("FOUND KEDB DATA:")
        print("="*50)
        print(f"ServicenowID: {result['ServicenowID']}")
        print(f"Short Description: {result['short_description']}")
        print(f"Description: {result['Description']}")
        print("="*50)
    else:
        print("No data found or error occurred.")

# Alternative function for direct usage without user input
def get_kedb_info(kedb_number):
    """
    Direct function to get KEDB info without user interaction
    
    Parameters:
    kedb_number (str): The KEDB number to search for
    
    Returns:
    dict: Dictionary containing the found data
    """
    excel_file = "kedb_data.xlsx"
    return find_kedb_data(excel_file, kedb_number)

if __name__ == "__main__":
    main()

# Example of direct usage:
# result = get_kedb_info("YOUR_KEDB_NUMBER")
# if result:
#     print(f"Short Description: {result['short_description']}")
#     print(f"Description: {result['Description']}")




# Search for a specific KEDB number
result = get_kedb_info("KB0012345")  # Replace with your actual KEDB number

if result:
    print(f"ServicenowID: {result['ServicenowID']}")
    print(f"Short Description: {result['short_description']}")
    print(f"Description: {result['Description']}")
