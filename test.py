import pandas as pd

def extract_excel_columns_by_position(file_path, sheet_name=None):
    """
    Extract columns by their Excel position (A, G, K, etc.)
    """
    
    # Column positions (0-based indexing)
    # A=0, G=6, K=10, M=12, O=14, R=17, V=21, X=23, Y=24, AF=31, AG=32
    column_positions = [23, 0, 6, 10, 12, 14, 17, 21, 24, 31, 32]  # X, A, G, K, M, O, R, V, Y, AF, AG
    
    try:
        # Read the Excel file
        if sheet_name:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        else:
            df = pd.read_excel(file_path)
        
        # Extract columns by position
        available_positions = [pos for pos in column_positions if pos < len(df.columns)]
        
        if available_positions:
            extracted_data = df.iloc[:, available_positions].copy()
            
            # Rename columns for clarity
            column_names = [
                'Resolution [AF KCS Article]', 'Number', 'Short description', 
                'Category', 'Meta', 'URL', 'Cause', 'Issue', 'Resolution', 
                'Use count', 'View count'
            ]
            
            # Only assign names for columns that were actually extracted
            extracted_data.columns = column_names[:len(available_positions)]
            
            return extracted_data
        else:
            print("No valid column positions found.")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return pd.DataFrame()

# Usage example
input_file = "your_excel_file.xlsx"
data = extract_excel_columns_by_position(input_file)
print(data.head())
