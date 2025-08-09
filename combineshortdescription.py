import pandas as pd
import os

def create_unique_kedb_with_unique_combined_descriptions(input_excel_path, output_excel_path):
    """
    Create a new Excel file with unique KEDB numbers and combined UNIQUE short descriptions
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
        
        # Remove empty descriptions and invalid entries
        df_clean = df_clean[df_clean['short_description'] != '']
        df_clean = df_clean[df_clean['short_description'].str.lower() != 'nan']
        df_clean = df_clean[df_clean['KEDB'] != '']
        df_clean = df_clean[df_clean['KEDB'].str.lower() != 'nan']
        
        print(f"🔍 Processing {len(df_clean)} valid records...")
        
        # Find duplicate KEDB numbers
        kedb_counts = df_clean['KEDB'].value_counts()
        duplicate_kedbs = kedb_counts[kedb_counts > 1]
        unique_kedbs = kedb_counts[kedb_counts == 1]
        
        print(f"📊 Analysis:")
        print(f"   • Unique KEDB numbers: {len(unique_kedbs)}")
        print(f"   • Duplicate KEDB numbers: {len(duplicate_kedbs)}")
        print(f"   • Total KEDB numbers after processing: {len(kedb_counts)}")
        
        # Enhanced function to combine UNIQUE descriptions only
        print(f"🔗 Removing duplicates and combining unique short descriptions for each KEDB...")
        
        def combine_unique_descriptions(group):
            """
            Remove duplicate descriptions and combine only unique ones
            """
            # Convert all descriptions to lowercase for comparison (case-insensitive deduplication)
            descriptions = group['short_description'].tolist()
            
            # Remove duplicates while preserving original case and order
            unique_descriptions = []
            seen_lower = set()
            
            for desc in descriptions:
                desc_lower = desc.lower().strip()
                if desc_lower not in seen_lower and desc_lower != '':
                    unique_descriptions.append(desc.strip())
                    seen_lower.add(desc_lower)
            
            # Combine unique descriptions with ' - ' separator
            combined = ' - '.join(unique_descriptions)
            return combined, len(descriptions), len(unique_descriptions)
        
        # Process each KEDB group
        processed_data = []
        
        for kedb, group in df_clean.groupby('KEDB'):
            combined_desc, original_count, unique_count = combine_unique_descriptions(group)
            
            # Get first occurrence for other columns
            first_row = group.iloc[0]
            
            processed_row = {
                'KEDB': kedb,
                'combined_unique_short_description': combined_desc,
                'original_record_count': original_count,
                'unique_descriptions_count': unique_count,
                'duplicates_removed': original_count - unique_count
            }
            
            # Add other columns from the first occurrence
            for col in df_clean.columns:
                if col not in ['KEDB', 'short_description']:
                    processed_row[col] = first_row[col]
            
            processed_data.append(processed_row)
        
        # Create DataFrame from processed data
        final_df = pd.DataFrame(processed_data)
        
        # Sort by KEDB
        final_df = final_df.sort_values('KEDB')
        
        # Save to new Excel file
        final_df.to_excel(output_excel_path, index=False)
        
        # Calculate statistics
        total_duplicates_removed = final_df['duplicates_removed'].sum()
        kedbs_with_duplicates = len(final_df[final_df['duplicates_removed'] > 0])
        
        print(f"\n✅ Processing complete!")
        print(f"📊 Final results:")
        print(f"   • Total unique KEDB numbers: {len(final_df)}")
        print(f"   • KEDBs with duplicate descriptions removed: {kedbs_with_duplicates}")
        print(f"   • Total duplicate descriptions removed: {total_duplicates_removed}")
        print(f"   • Records with single descriptions: {len(final_df[final_df['original_record_count'] == 1])}")
        print(f"💾 New Excel file created: {output_excel_path}")
        
        # Show sample of results
        print(f"\n📋 Sample Results:")
        display_columns = ['KEDB', 'combined_unique_short_description', 'original_record_count', 'unique_descriptions_count', 'duplicates_removed']
        available_columns = [col for col in display_columns if col in final_df.columns]
        print(final_df[available_columns].head(10).to_string(index=False, max_colwidth=50))
        
        # Show examples of duplicate removal
        duplicate_examples = final_df[final_df['duplicates_removed'] > 0].head(3)
        if len(duplicate_examples) > 0:
            print(f"\n🔍 Examples of Duplicate Removal:")
            for _, row in duplicate_examples.iterrows():
                print(f"KEDB: {row['KEDB']}")
                print(f"Original records: {row['original_record_count']}")
                print(f"Unique descriptions: {row['unique_descriptions_count']}")
                print(f"Duplicates removed: {row['duplicates_removed']}")
                print(f"Combined: {row['combined_unique_short_description'][:100]}...")
                print("-" * 60)
        
        # Show examples where no duplicates were found
        no_duplicates = final_df[final_df['duplicates_removed'] == 0].head(2)
        if len(no_duplicates) > 0:
            print(f"\n✅ Examples with No Duplicates:")
            for _, row in no_duplicates.iterrows():
                print(f"KEDB: {row['KEDB']} - {row['unique_descriptions_count']} unique description(s)")
        
        return final_df
        
    except FileNotFoundError:
        print(f"❌ Error: Excel file '{input_excel_path}' not found!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def create_detailed_duplicate_analysis(final_df, analysis_output_path):
    """
    Create detailed analysis focusing on duplicate removal process
    """
    
    try:
        # Overall statistics
        total_kedbs = len(final_df)
        total_original_records = final_df['original_record_count'].sum()
        total_unique_descriptions = final_df['unique_descriptions_count'].sum()
        total_duplicates_removed = final_df['duplicates_removed'].sum()
        kedbs_with_duplicates = len(final_df[final_df['duplicates_removed'] > 0])
        
        # Duplicate removal efficiency
        duplicate_removal_rate = (total_duplicates_removed / total_original_records * 100) if total_original_records > 0 else 0
        
        # Analysis summary
        summary_data = [{
            'Metric': 'Total Unique KEDB Numbers',
            'Value': total_kedbs
        }, {
            'Metric': 'Total Original Records',
            'Value': total_original_records
        }, {
            'Metric': 'Total Unique Descriptions After Deduplication',
            'Value': total_unique_descriptions
        }, {
            'Metric': 'Total Duplicate Descriptions Removed',
            'Value': total_duplicates_removed
        }, {
            'Metric': 'KEDBs with Duplicates Removed',
            'Value': kedbs_with_duplicates
        }, {
            'Metric': 'Duplicate Removal Rate (%)',
            'Value': round(duplicate_removal_rate, 2)
        }]
        
        # Distribution of duplicates removed
        duplicate_distribution = final_df['duplicates_removed'].value_counts().sort_index().reset_index()
        duplicate_distribution.columns = ['Duplicates_Removed', 'Count_of_KEDBs']
        
        # Top KEDBs with most duplicates removed
        top_duplicates_removed = final_df[final_df['duplicates_removed'] > 0].nlargest(10, 'duplicates_removed')[
            ['KEDB', 'original_record_count', 'unique_descriptions_count', 'duplicates_removed', 'combined_unique_short_description']
        ].copy()
        
        # KEDBs with high duplicate ratios
        final_df_with_ratio = final_df.copy()
        final_df_with_ratio['duplicate_ratio'] = (final_df_with_ratio['duplicates_removed'] / final_df_with_ratio['original_record_count']) * 100
        high_duplicate_ratio = final_df_with_ratio[final_df_with_ratio['duplicate_ratio'] > 0].nlargest(10, 'duplicate_ratio')[
            ['KEDB', 'original_record_count', 'unique_descriptions_count', 'duplicates_removed', 'duplicate_ratio']
        ].copy()
        high_duplicate_ratio['duplicate_ratio'] = high_duplicate_ratio['duplicate_ratio'].round(2)
        
        # Save analysis to Excel
        with pd.ExcelWriter(analysis_output_path, engine='openpyxl') as writer:
            # Summary sheet
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Duplicate_Removal_Summary', index=False)
            
            # Duplicate distribution
            duplicate_distribution.to_excel(writer, sheet_name='Duplicate_Distribution', index=False)
            
            # Top duplicates removed
            top_duplicates_removed.to_excel(writer, sheet_name='Top_Duplicates_Removed', index=False)
            
            # High duplicate ratios
            high_duplicate_ratio.to_excel(writer, sheet_name='High_Duplicate_Ratios', index=False)
            
            # Full processed data (first 1000 rows)
            final_df.head(1000).to_excel(writer, sheet_name='Processed_Data_Sample', index=False)
        
        print(f"📊 Detailed duplicate removal analysis saved to: {analysis_output_path}")
        
        return {
            'total_duplicates_removed': total_duplicates_removed,
            'duplicate_removal_rate': duplicate_removal_rate,
            'kedbs_with_duplicates': kedbs_with_duplicates
        }
        
    except Exception as e:
        print(f"❌ Error creating analysis: {str(e)}")
        return None

def demonstrate_duplicate_removal(input_excel_path):
    """
    Show examples of how duplicate removal will work
    """
    
    try:
        df = pd.read_excel(input_excel_path)
        
        if 'KEDB' not in df.columns or 'short_description' not in df.columns:
            return
        
        # Find a KEDB with duplicates to demonstrate
        df_clean = df.dropna(subset=['KEDB', 'short_description'])
        df_clean['KEDB'] = df_clean['KEDB'].astype(str).str.strip()
        df_clean['short_description'] = df_clean['short_description'].astype(str).str.strip()
        
        kedb_counts = df_clean['KEDB'].value_counts()
        duplicate_kedbs = kedb_counts[kedb_counts > 1].head(3)
        
        if len(duplicate_kedbs) > 0:
            print(f"\n🔍 DUPLICATE REMOVAL DEMONSTRATION:")
            print("=" * 60)
            
            for kedb in duplicate_kedbs.index:
                kedb_records = df_clean[df_clean['KEDB'] == kedb]
                descriptions = kedb_records['short_description'].tolist()
                
                print(f"\nKEDB: {kedb}")
                print(f"Original descriptions ({len(descriptions)}):")
                for i, desc in enumerate(descriptions, 1):
                    print(f"  {i}. {desc}")
                
                # Show unique descriptions
                unique_descriptions = []
                seen_lower = set()
                for desc in descriptions:
                    desc_lower = desc.lower().strip()
                    if desc_lower not in seen_lower:
                        unique_descriptions.append(desc.strip())
                        seen_lower.add(desc_lower)
                
                print(f"\nAfter removing duplicates ({len(unique_descriptions)}):")
                for i, desc in enumerate(unique_descriptions, 1):
                    print(f"  {i}. {desc}")
                
                combined = ' - '.join(unique_descriptions)
                print(f"\nCombined result:")
                print(f"  {combined}")
                print("-" * 60)
        
    except Exception as e:
        print(f"❌ Error in demonstration: {str(e)}")

# Main execution
if __name__ == "__main__":
    # File paths - UPDATE THESE TO YOUR ACTUAL PATHS
    input_excel = "shee1.xlsx"  # Your input Excel file
    output_excel = "unique_kedb_unique_combined_descriptions.xlsx"
    analysis_excel = "duplicate_removal_analysis.xlsx"
    
    print("🚀 Starting KEDB Unique Description Combination Process...")
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
    
    # Demonstrate duplicate removal
    print("🔍 Analyzing duplicate patterns in your data...")
    demonstrate_duplicate_removal(input_excel)
    
    # Ask for confirmation
    print(f"\n❓ Proceed with removing duplicate descriptions and combining unique ones? (y/n): ", end="")
    confirmation = input().lower().strip()
    
    if confirmation in ['y', 'yes']:
        # Process the data
        result_df = create_unique_kedb_with_unique_combined_descriptions(input_excel, output_excel)
        
        if result_df is not None:
            # Create detailed analysis
            analysis_stats = create_detailed_duplicate_analysis(result_df, analysis_excel)
            
            print("\n" + "=" * 70)
            print("🎉 ENHANCED KEDB PROCESSING COMPLETE!")
            print(f"📊 Main output: {output_excel}")
            print(f"📈 Analysis report: {analysis_excel}")
            
            if analysis_stats:
                print(f"\n✅ Duplicate Removal Summary:")
                print(f"   • Total duplicates removed: {analysis_stats['total_duplicates_removed']}")
                print(f"   • Duplicate removal rate: {analysis_stats['duplicate_removal_rate']:.2f}%")
                print(f"   • KEDBs with duplicates cleaned: {analysis_stats['kedbs_with_duplicates']}")
                print(f"   • Final unique KEDB records: {len(result_df)}")
            
    else:
        print("❌ Process cancelled by user.")
