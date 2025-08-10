import pandas as pd
import os

def simple_kedb_duplicate_removal(input_file, output_file):
    """
    Simple script to remove duplicate short descriptions by KEDB and combine them
    """
    
    try:
        # Read the Excel file
        print("📊 Reading KEDB_inc.xlsx...")
        df = pd.read_excel(input_file)
        
        print(f"📄 Loaded {len(df)} records")
        print(f"📋 Columns found: {list(df.columns)}")
        
        # Find the correct column names (case-insensitive search)
        kedb_col = None
        desc_col = None
        
        for col in df.columns:
            col_lower = col.lower().strip()
            if 'kedb' in col_lower:
                kedb_col = col
                print(f"✅ Found KEDB column: '{col}'")
            if 'short' in col_lower and 'description' in col_lower:
                desc_col = col
                print(f"✅ Found description column: '{col}'")
        
        # Check if columns were found
        if kedb_col is None:
            print("❌ Error: No KEDB column found. Available columns:")
            for i, col in enumerate(df.columns, 1):
                print(f"  {i}. {col}")
            return None
            
        if desc_col is None:
            print("❌ Error: No short_description column found. Available columns:")
            for i, col in enumerate(df.columns, 1):
                print(f"  {i}. {col}")
            return None
        
        # Clean data using the found column names
        print(f"🔍 Using columns: KEDB='{kedb_col}', Description='{desc_col}'")
        
        df_clean = df[[kedb_col, desc_col]].copy()
        df_clean = df_clean.dropna(subset=[kedb_col, desc_col])
        
        # Rename columns for easier processing
        df_clean.columns = ['KEDB', 'short_description']
        
        # Convert to string and clean
        df_clean['KEDB'] = df_clean['KEDB'].astype(str).str.strip()
        df_clean['short_description'] = df_clean['short_description'].astype(str).str.strip()
        
        # Remove empty descriptions
        df_clean = df_clean[df_clean['short_description'] != '']
        df_clean = df_clean[df_clean['short_description'].str.lower() != 'nan']
        df_clean = df_clean[df_clean['KEDB'] != '']
        df_clean = df_clean[df_clean['KEDB'].str.lower() != 'nan']
        
        print(f"🔍 Processing {len(df_clean)} valid records")
        
        # Show sample data before processing
        print(f"\n📋 Sample data being processed:")
        print(df_clean.head(3).to_string(index=False))
        
        # Group by KEDB and combine unique descriptions
        print(f"\n🔗 Combining unique descriptions by KEDB...")
        
        result_data = []
        
        for kedb, group in df_clean.groupby('KEDB'):
            descriptions = group['short_description'].tolist()
            
            # Remove duplicates (case-insensitive) while preserving order
            unique_descriptions = []
            seen = set()
            
            for desc in descriptions:
                desc_lower = desc.lower().strip()
                if desc_lower not in seen and desc_lower:
                    unique_descriptions.append(desc.strip())
                    seen.add(desc_lower)
            
            combined = ' - '.join(unique_descriptions)
            
            result_data.append({
                'KEDB': kedb,
                'combined_short_description': combined
            })
        
        # Create result DataFrame
        result_df = pd.DataFrame(result_data)
        result_df = result_df.sort_values('KEDB')
        
        # Save to Excel
        result_df.to_excel(output_file, sheet_name='Combined_KEDB_Data', index=False)
        
        print(f"\n✅ Processing complete!")
        print(f"📊 Results: {len(result_df)} unique KEDB numbers")
        print(f"💾 Output saved to: {output_file}")
        
        # Show sample results
        print(f"\n📋 Sample Results:")
        for i, (_, row) in enumerate(result_df.head(5).iterrows()):
            print(f"{i+1}. KEDB: {row['KEDB']}")
            print(f"   Combined: {row['combined_short_description'][:100]}...")
            print()
        
        return result_df
        
    except Exception as e:
        print(f"❌ Error at processing step: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        
        # Additional debug info
        try:
            print(f"\n🔍 Debug Info:")
            if 'df' in locals():
                print(f"   • DataFrame shape: {df.shape}")
                print(f"   • DataFrame columns: {list(df.columns)}")
            if 'df_clean' in locals():
                print(f"   • Clean DataFrame shape: {df_clean.shape}")
        except:
            pass
        
        return None

def check_excel_file_structure(input_file):
    """
    Check the structure of the Excel file to help diagnose issues
    """
    
    try:
        print("🔍 Checking Excel file structure...")
        
        # Try to read just the first few rows
        df_sample = pd.read_excel(input_file, nrows=5)
        
        print(f"📊 File Analysis:")
        print(f"   • Sample rows read: {len(df_sample)}")
        print(f"   • Total columns: {len(df_sample.columns)}")
        
        print(f"\n📋 Column Names:")
        for i, col in enumerate(df_sample.columns, 1):
            print(f"   {i:2d}. '{col}' (Type: {df_sample[col].dtype})")
        
        # Check for KEDB-like columns
        kedb_candidates = []
        desc_candidates = []
        
        for col in df_sample.columns:
            col_lower = str(col).lower()
            if 'kedb' in col_lower or 'kb' in col_lower:
                kedb_candidates.append(col)
            if 'description' in col_lower or 'desc' in col_lower:
                desc_candidates.append(col)
        
        print(f"\n🎯 Potential matches:")
        print(f"   • KEDB candidates: {kedb_candidates}")
        print(f"   • Description candidates: {desc_candidates}")
        
        print(f"\n📋 Sample data:")
        print(df_sample.to_string(index=False, max_colwidth=30))
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking file structure: {str(e)}")
        return False

# Main execution
if __name__ == "__main__":
    input_file = "KEDB_inc.xlsx"
    output_file = "KEDB_combined_simple.xlsx"
    
    print("🚀 Fixed Simple KEDB Duplicate Removal & Combination")
    print("=" * 60)
    
    if not os.path.exists(input_file):
        print(f"❌ {input_file} not found!")
        print("\n📁 Excel files in current directory:")
        for file in os.listdir('.'):
            if file.endswith(('.xlsx', '.xls')):
                print(f"   - {file}")
        exit(1)
    
    # First check the file structure
    if check_excel_file_structure(input_file):
        print("\n" + "=" * 60)
        
        # Ask if user wants to proceed
        proceed = input("❓ Proceed with processing? (y/n): ").lower().strip()
        
        if proceed in ['y', 'yes']:
            result = simple_kedb_duplicate_removal(input_file, output_file)
            
            if result is not None:
                print(f"\n🎉 SUCCESS! Check {output_file}")
            else:
                print(f"\n❌ Processing failed. Please check the column names above.")
        else:
            print("❌ Processing cancelled.")
    else:
        print("❌ Cannot proceed due to file structure issues.")
