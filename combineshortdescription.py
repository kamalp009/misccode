import pandas as pd
import os

def create_unique_kedb_with_combined_descriptions(input_excel_path, output_excel_path):
    """
    Create a new Excel file with unique KEDB numbers and combined short descriptions
    """
    
    try:
        # Read the Excel file
        print("📊 Reading Excel file...")
        df = pd.read_excel(input_excel_path)
        
        # Check if required columns exist
        if 'KEDB' not in df.columns:
            print("❌ Error: 'KEDB' column not found in Excel file")
            return None
            
        if 'short_description' not in df.columns:
            print("❌ Error: 'short_description' column not found in Excel file")
            return None
        
        print(f"📄 Original data loaded: {len(df)} records")
        
        # Remove rows where KEDB or short_description is null
        df_clean = df.dropna(subset=['KEDB', 'short_description']).copy()
        print(f"📝 Clean data after removing nulls: {len(df_clean)} records")
        
        # Convert KEDB to string and clean whitespace
        df_clean['KEDB'] = df_clean['KEDB'].astype(str).str.strip()
        df_clean['short_description'] = df_clean['short_description'].astype(str).str.strip()
        
        # Remove empty descriptions
        df_clean = df_clean[df_clean['short_description'] != '']
        df_clean = df_clean[df_clean['short_description'].str.lower() != 'nan']
        
        print(f"🔍 Processing {len(df_clean)} valid records...")
        
        # Find duplicate KEDB numbers
        kedb_counts = df_clean['KEDB'].value_counts()
        duplicate_kedbs = kedb_counts[kedb_counts > 1]
        unique_kedbs = kedb_counts[kedb_counts == 1]
        
        print(f"📊 Analysis:")
        print(f"   • Unique KEDB numbers: {len(unique_kedbs)}")
        print(f"   • Duplicate KEDB numbers: {len(duplicate_kedbs)}")
        print(f"   • Total KEDB numbers after processing: {len(kedb_counts)}")
        
        # Group by KEDB and combine short descriptions
        print(f"🔗 Combining short descriptions for duplicate KEDBs...")
        
        def combine_descriptions(group):
            # Get unique descriptions (remove duplicates)
            unique_descriptions = group['short_description'].drop_duplicates().tolist()
            # Combine with ' - ' separator
            combined = ' - '.join(unique_descriptions)
            return combined
        
        # Group by KEDB and combine descriptions
        kedb_grouped = df_clean.groupby('KEDB').agg({
            'short_description': combine_descriptions
        }).reset_index()
        
        # Rename the column for clarity
        kedb_grouped.rename(columns={'short_description': 'combined_short_description'}, inplace=True)
        
        # Add additional statistics
        kedb_grouped['original_record_count'] = df_clean.groupby('KEDB').size().values
        kedb_grouped['unique_descriptions_count'] = df_clean.groupby('KEDB')['short_description'].nunique().values
        
        # Add other columns from original data (take first occurrence for each KEDB)
        other_columns = [col for col in df_clean.columns if col not in ['KEDB', 'short_description']]
        
        if other_columns:
            # Get first occurrence of each KEDB for other columns
            first_occurrence = df_clean.groupby('KEDB').first()[other_columns].reset_index()
            
            # Merge with the grouped data
            final_df = pd.merge(kedb_grouped, first_occurrence, on='KEDB', how='left')
        else:
            final_df = kedb_grouped
        
        # Sort by KEDB
        final_df = final_df.sort_values('KEDB')
        
        # Save to new Excel file
        final_df.to_excel(output_excel_path, index=False)
        
        print(f"\n✅ Processing complete!")
        print(f"📊 Final results:")
        print(f"   • Total unique KEDB numbers: {len(final_df)}")
        print(f"   • Records with combined descriptions: {len(final_df[final_df['original_record_count'] > 1])}")
        print(f"   • Records with single descriptions: {len(final_df[final_df['original_record_count'] == 1])}")
        print(f"💾 New Excel file created: {output_excel_path}")
        
        # Show sample of results
        print(f"\n📋 Sample Results:")
        display_columns = ['KEDB', 'combined_short_description', 'original_record_count']
        print(final_df[display_columns].head(10).to_string(index=False))
        
        # Show examples of combined descriptions
        combined_examples = final_df[final_df['original_record_count'] > 1].head(3)
        if len(combined_examples) > 0:
            print(f"\n🔗 Examples of Combined Descriptions:")
            for _, row in combined_examples.iterrows():
                print(f"KEDB: {row['KEDB']}")
                print(f"Combined: {row['combined_short_description'][:100]}...")
                print(f"Original count: {row['original_record_count']}")
                print("-" * 50)
        
        return final_df
        
    except FileNotFoundError:
        print(f"❌ Error: Excel file '{input_excel_path}' not found!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def create_detailed_analysis(final_df, analysis_output_path):
    """
    Create detailed analysis of the KEDB combination process
    """
    
    try:
        # Create analysis data
        analysis_data = []
        
        # Overall statistics
        total_kedbs = len(final_df)
        duplicated_kedbs = len(final_df[final_df['original_record_count'] > 1])
        unique_kedbs = len(final_df[final_df['original_record_count'] == 1])
        max_combinations = final_df['original_record_count'].max()
        avg_combinations = final_df['original_record_count'].mean()
        
        # KEDB with most combinations
        most_combined = final_df.loc[final_df['original_record_count'].idxmax()]
        
        # Analysis summary
        summary_data = [{
            'Metric': 'Total Unique KEDB Numbers',
            'Value': total_kedbs
        }, {
            'Metric': 'KEDBs with Multiple Descriptions',
            'Value': duplicated_kedbs
        }, {
            'Metric': 'KEDBs with Single Description',
            'Value': unique_kedbs
        }, {
            'Metric': 'Maximum Descriptions Combined',
            'Value': max_combinations
        }, {
            'Metric': 'Average Descriptions per KEDB',
            'Value': round(avg_combinations, 2)
        }, {
            'Metric': 'KEDB with Most Combinations',
            'Value': most_combined['KEDB']
        }]
        
        # Distribution analysis
        distribution_data = final_df['original_record_count'].value_counts().sort_index().reset_index()
        distribution_data.columns = ['Number_of_Descriptions', 'Count_of_KEDBs']
        
        # Top KEDBs with most combinations
        top_combinations = final_df.nlargest(10, 'original_record_count')[
            ['KEDB', 'combined_short_description', 'original_record_count', 'unique_descriptions_count']
        ].copy()
        
        # Save analysis to Excel
        with pd.ExcelWriter(analysis_output_path, engine='openpyxl') as writer:
            # Summary sheet
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary_Statistics', index=False)
            
            # Distribution sheet
            distribution_data.to_excel(writer, sheet_name='Description_Distribution', index=False)
            
            # Top combinations sheet
            top_combinations.to_excel(writer, sheet_name='Top_Combinations', index=False)
            
            # Full data sheet (first 1000 rows to avoid Excel limits)
            final_df.head(1000).to_excel(writer, sheet_name='Sample_Data', index=False)
        
        print(f"📊 Detailed analysis saved to: {analysis_output_path}")
        
    except Exception as e:
        print(f"❌ Error creating analysis: {str(e)}")

def validate_and_preview_data(input_excel_path):
    """
    Preview the input data to understand the structure
    """
    
    try:
        df = pd.read_excel(input_excel_path)
        
        print("🔍 DATA PREVIEW:")
        print("=" * 50)
        print(f"Total rows: {len(df)}")
        print(f"Total columns: {len(df.columns)}")
        print("\nColumns found:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i}. {col}")
        
        if 'KEDB' in df.columns and 'short_description' in df.columns:
            kedb_stats = df['KEDB'].value_counts()
            duplicates = kedb_stats[kedb_stats > 1]
            
            print(f"\nKEDB Analysis:")
            print(f"  • Total KEDB entries: {len(df)}")
            print(f"  • Unique KEDB numbers: {df['KEDB'].nunique()}")
            print(f"  • Duplicate KEDB numbers: {len(duplicates)}")
            
            if len(duplicates) > 0:
                print(f"  • Top 5 most duplicated KEDBs:")
                for kedb, count in duplicates.head().items():
                    print(f"    - {kedb}: {count} times")
            
            print(f"\nSample data:")
            print(df[['KEDB', 'short_description']].head().to_string(index=False))
        
        return True
        
    except Exception as e:
        print(f"❌ Error previewing data: {str(e)}")
        return False

# Main execution
if __name__ == "__main__":
    # File paths - UPDATE THESE TO YOUR ACTUAL PATHS
    input_excel = "shee1.xlsx"  # Your input Excel file
    output_excel = "unique_kedb_combined_descriptions.xlsx"
    analysis_excel = "kedb_combination_analysis.xlsx"
    
    print("🚀 Starting KEDB Description Combination Process...")
    print("=" * 70)
    
    # Check if input file exists
    if not os.path.exists(input_excel):
        print(f"❌ Error: Input Excel file '{input_excel}' not found!")
        print("Please update the 'input_excel' variable with the correct path.")
        
        # Show available Excel files
        print(f"\n📁 Excel files in current directory:")
        for file in os.listdir('.'):
            if file.endswith(('.xlsx', '.xls')):
                print(f"  - {file}")
        exit(1)
    
    # Preview the data first
    print("🔍 Previewing input data...")
    if validate_and_preview_data(input_excel):
        
        # Ask for confirmation
        print(f"\n❓ Proceed with combining descriptions for duplicate KEDB numbers? (y/n): ", end="")
        confirmation = input().lower().strip()
        
        if confirmation in ['y', 'yes']:
            # Process the data
            result_df = create_unique_kedb_with_combined_descriptions(input_excel, output_excel)
            
            if result_df is not None:
                # Create detailed analysis
                create_detailed_analysis(result_df, analysis_excel)
                
                print("\n" + "=" * 70)
                print("🎉 KEDB COMBINATION PROCESS COMPLETE!")
                print(f"📊 Main output: {output_excel}")
                print(f"📈 Analysis report: {analysis_excel}")
                
                print(f"\n✅ Summary:")
                print(f"   • Created {len(result_df)} unique KEDB records")
                print(f"   • Combined descriptions using ' - ' separator")
                print(f"   • Preserved all other column data")
                
        else:
            print("❌ Process cancelled by user.")
    
    else:
        print("❌ Cannot proceed due to data preview errors.")
