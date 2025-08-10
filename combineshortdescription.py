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
        
        # Check required columns
        if 'KEDB' not in df.columns or 'short_description' not in df.columns:
            print("❌ Error: Required columns 'KEDB' and 'short_description' not found")
            return None
        
        print(f"📄 Loaded {len(df)} records")
        
        # Clean data
        df_clean = df.dropna(subset=['KEDB', 'short_description']).copy()
        df_clean['KEDB'] = df_clean['KEDB'].astype(str).str.strip()
        df_clean['short_description'] = df_clean['short_description'].astype(str).str.strip()
        
        # Remove empty descriptions
        df_clean = df_clean[df_clean['short_description'] != '']
        df_clean = df_clean[df_clean['short_description'].str.lower() != 'nan']
        
        print(f"🔍 Processing {len(df_clean)} valid records")
        
        # Group by KEDB and combine unique descriptions
        def combine_unique_descriptions(group):
            # Get unique descriptions (case-insensitive)
            descriptions = group['short_description'].tolist()
            unique_descriptions = []
            seen = set()
            
            for desc in descriptions:
                desc_lower = desc.lower().strip()
                if desc_lower not in seen:
                    unique_descriptions.append(desc.strip())
                    seen.add(desc_lower)
            
            return ' - '.join(unique_descriptions)
        
        # Apply grouping and combination
        result = df_clean.groupby('KEDB').agg({
            'short_description': combine_unique_descriptions
        }).reset_index()
        
        result.rename(columns={'short_description': 'combined_short_description'}, inplace=True)
        
        # Save to Excel
        result.to_excel(output_file, sheet_name='Combined_KEDB_Data', index=False)
        
        print(f"✅ Processing complete!")
        print(f"📊 Results: {len(result)} unique KEDB numbers")
        print(f"💾 Output saved to: {output_file}")
        
        # Show sample
        print(f"\n📋 Sample Results:")
        print(result.head(10).to_string(index=False, max_colwidth=80))
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

# Main execution
if __name__ == "__main__":
    input_file = "KEDB_inc.xlsx"
    output_file = "KEDB_combined_simple.xlsx"
    
    print("🚀 Simple KEDB Duplicate Removal & Combination")
    print("=" * 50)
    
    if not os.path.exists(input_file):
        print(f"❌ {input_file} not found!")
        exit(1)
    
    simple_kedb_duplicate_removal(input_file, output_file)
