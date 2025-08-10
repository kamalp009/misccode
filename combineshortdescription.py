import pandas as pd
import os

def process_kedb_inc_with_unique_descriptions(input_excel_path, output_excel_path):
    """
    Read KEDB_inc.xlsx, remove duplicate short descriptions within each KEDB group,
    combine unique descriptions, and output to different sheets
    """
    
    try:
        # Read the Excel file
        print("📊 Reading KEDB_inc.xlsx...")
        df = pd.read_excel(input_excel_path)
        
        print(f"📄 Original data loaded: {len(df)} records")
        print(f"📋 Columns found: {list(df.columns)}")
        
        # Check if required columns exist
        if 'KEDB' not in df.columns:
            print("❌ Error: 'KEDB' column not found in KEDB_inc.xlsx")
            return None
            
        if 'short_description' not in df.columns:
            print("❌ Error: 'short_description' column not found in KEDB_inc.xlsx")
            return None
        
        # Remove rows where KEDB or short_description is null
        df_clean = df.dropna(subset=['KEDB', 'short_description']).copy()
        print(f"📝 Clean data after removing nulls: {len(df_clean)} records")
        
        # Convert to string and clean whitespace
        df_clean['KEDB'] = df_clean['KEDB'].astype(str).str.strip()
        df_clean['short_description'] = df_clean['short_description'].astype(str).str.strip()
        
        # Remove empty and invalid entries
        df_clean = df_clean[df_clean['short_description'] != '']
        df_clean = df_clean[df_clean['short_description'].str.lower() != 'nan']
        df_clean = df_clean[df_clean['KEDB'] != '']
        df_clean = df_clean[df_clean['KEDB'].str.lower() != 'nan']
        
        print(f"🔍 Processing {len(df_clean)} valid records...")
        
        # Analyze KEDB distribution
        kedb_counts = df_clean['KEDB'].value_counts()
        duplicate_kedbs = kedb_counts[kedb_counts > 1]
        
        print(f"📊 KEDB Analysis:")
        print(f"   • Total KEDB entries: {len(df_clean)}")
        print(f"   • Unique KEDB numbers: {len(kedb_counts)}")
        print(f"   • KEDB numbers with multiple entries: {len(duplicate_kedbs)}")
        
        # Function to remove duplicates and combine descriptions
        def process_kedb_group(group):
            """
            Remove duplicate short descriptions within a KEDB group and combine unique ones
            """
            descriptions = group['short_description'].tolist()
            
            # Remove duplicates (case-insensitive) while preserving original case and order
            unique_descriptions = []
            seen_lower = set()
            
            for desc in descriptions:
                desc_clean = desc.strip()
                desc_lower = desc_clean.lower()
                
                if desc_lower not in seen_lower and desc_lower != '':
                    unique_descriptions.append(desc_clean)
                    seen_lower.add(desc_lower)
            
            # Combine unique descriptions with ' - '
            combined_description = ' - '.join(unique_descriptions)
            
            # Get first row for other columns
            first_row = group.iloc[0].copy()
            
            # Create result row
            result = {
                'KEDB': first_row['KEDB'],
                'combined_short_description': combined_description,
                'original_entries_count': len(descriptions),
                'unique_descriptions_count': len(unique_descriptions),
                'duplicates_removed': len(descriptions) - len(unique_descriptions)
            }
            
            # Add other columns from first occurrence
            for col in df_clean.columns:
                if col not in ['KEDB', 'short_description']:
                    result[f'first_occurrence_{col}'] = first_row[col]
            
            return pd.Series(result)
        
        print(f"🔗 Removing duplicates and combining descriptions by KEDB...")
        
        # Process each KEDB group
        processed_df = df_clean.groupby('KEDB').apply(process_kedb_group).reset_index(drop=True)
        
        # Sort by KEDB
        processed_df = processed_df.sort_values('KEDB')
        
        # Create detailed breakdown for analysis
        breakdown_data = []
        for kedb in df_clean['KEDB'].unique():
            kedb_group = df_clean[df_clean['KEDB'] == kedb]
            descriptions = kedb_group['short_description'].tolist()
            
            breakdown_data.append({
                'KEDB': kedb,
                'total_entries': len(descriptions),
                'all_descriptions': ' | '.join(descriptions),  # Show all original descriptions
                'unique_count': len(set([d.lower().strip() for d in descriptions])),
                'has_duplicates': len(descriptions) != len(set([d.lower().strip() for d in descriptions]))
            })
        
        breakdown_df = pd.DataFrame(breakdown_data)
        breakdown_df = breakdown_df.sort_values('total_entries', ascending=False)
        
        # Save to Excel with multiple sheets
        with pd.ExcelWriter(output_excel_path, engine='openpyxl') as writer:
            # Main processed data sheet
            processed_df.to_excel(writer, sheet_name='Processed_KEDB_Data', index=False)
            
            # Original data sheet
            df_clean.to_excel(writer, sheet_name='Original_Data', index=False)
            
            # Detailed breakdown sheet
            breakdown_df.to_excel(writer, sheet_name='KEDB_Breakdown_Analysis', index=False)
            
            # Summary statistics sheet
            create_kedb_summary_stats(processed_df, breakdown_df, writer)
            
            # Examples sheet showing before/after
            create_examples_sheet(df_clean, processed_df, writer)
        
        # Calculate and display results
        total_duplicates_removed = processed_df['duplicates_removed'].sum()
        kedbs_with_duplicates = len(processed_df[processed_df['duplicates_removed'] > 0])
        
        print(f"\n✅ Processing complete!")
        print(f"📊 Results Summary:")
        print(f"   • Unique KEDB numbers processed: {len(processed_df)}")
        print(f"   • Total duplicate descriptions removed: {total_duplicates_removed}")
        print(f"   • KEDB numbers with duplicates cleaned: {kedbs_with_duplicates}")
        print(f"   • Average descriptions per KEDB: {processed_df['unique_descriptions_count'].mean():.2f}")
        print(f"💾 Output saved to: {output_excel_path}")
        
        # Display sample results
        print(f"\n📋 Sample Processed Results:")
        sample_columns = ['KEDB', 'combined_short_description', 'original_entries_count', 'unique_descriptions_count', 'duplicates_removed']
        available_columns = [col for col in sample_columns if col in processed_df.columns]
        print(processed_df[available_columns].head(8).to_string(index=False, max_colwidth=60))
        
        # Show examples of duplicate removal
        duplicates_examples = processed_df[processed_df['duplicates_removed'] > 0].head(3)
        if len(duplicates_examples) > 0:
            print(f"\n🔍 Examples of Duplicate Removal:")
            for _, row in duplicates_examples.iterrows():
                print(f"\nKEDB: {row['KEDB']}")
                print(f"Original entries: {row['original_entries_count']} → Unique: {row['unique_descriptions_count']} (Removed: {row['duplicates_removed']})")
                print(f"Combined: {row['combined_short_description'][:100]}...")
                print("-" * 80)
        
        return processed_df, breakdown_df
        
    except FileNotFoundError:
        print(f"❌ Error: KEDB_inc.xlsx file not found!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None, None

def create_kedb_summary_stats(processed_df, breakdown_df, writer):
    """Create summary statistics sheet"""
    
    try:
        # Overall statistics
        total_kedbs = len(processed_df)
        total_original_entries = processed_df['original_entries_count'].sum()
        total_unique_descriptions = processed_df['unique_descriptions_count'].sum()
        total_duplicates_removed = processed_df['duplicates_removed'].sum()
        kedbs_with_duplicates = len(processed_df[processed_df['duplicates_removed'] > 0])
        
        # Calculate efficiency metrics
        deduplication_rate = (total_duplicates_removed / total_original_entries * 100) if total_original_entries > 0 else 0
        avg_descriptions_per_kedb = total_unique_descriptions / total_kedbs if total_kedbs > 0 else 0
        
        summary_stats = [
            {'Metric': 'Total KEDB Numbers', 'Value': total_kedbs},
            {'Metric': 'Total Original Entries', 'Value': total_original_entries},
            {'Metric': 'Total Unique Descriptions', 'Value': total_unique_descriptions},
            {'Metric': 'Total Duplicates Removed', 'Value': total_duplicates_removed},
            {'Metric': 'KEDBs with Duplicates Cleaned', 'Value': kedbs_with_duplicates},
            {'Metric': 'Deduplication Rate (%)', 'Value': f"{deduplication_rate:.2f}%"},
            {'Metric': 'Avg Descriptions per KEDB', 'Value': f"{avg_descriptions_per_kedb:.2f}"},
        ]
        
        # Distribution analysis
        distribution_data = processed_df['unique_descriptions_count'].value_counts().sort_index().reset_index()
        distribution_data.columns = ['Unique_Descriptions_Count', 'Number_of_KEDBs']
        
        # Top KEDBs with most entries
        top_kedbs = processed_df.nlargest(10, 'original_entries_count')[
            ['KEDB', 'original_entries_count', 'unique_descriptions_count', 'duplicates_removed']
        ]
        
        # Save to different sheets
        pd.DataFrame(summary_stats).to_excel(writer, sheet_name='Summary_Statistics', index=False)
        distribution_data.to_excel(writer, sheet_name='Description_Distribution', index=False)
        top_kedbs.to_excel(writer, sheet_name='Top_KEDBs_by_Entries', index=False)
        
    except Exception as e:
        print(f"⚠️ Warning: Could not create summary stats - {str(e)}")

def create_examples_sheet(original_df, processed_df, writer):
    """Create examples sheet showing before and after"""
    
    try:
        examples_data = []
        
        # Get KEDBs with duplicates for examples
        kedbs_with_duplicates = processed_df[processed_df['duplicates_removed'] > 0]['KEDB'].head(5)
        
        for kedb in kedbs_with_duplicates:
            # Original descriptions
            original_descriptions = original_df[original_df['KEDB'] == kedb]['short_description'].tolist()
            processed_row = processed_df[processed_df['KEDB'] == kedb].iloc[0]
            
            examples_data.append({
                'KEDB': kedb,
                'original_count': len(original_descriptions),
                'original_descriptions': ' | '.join(original_descriptions),
                'unique_count': processed_row['unique_descriptions_count'],
                'combined_unique_descriptions': processed_row['combined_short_description'],
                'duplicates_removed': processed_row['duplicates_removed']
            })
        
        if examples_data:
            examples_df = pd.DataFrame(examples_data)
            examples_df.to_excel(writer, sheet_name='Before_After_Examples', index=False)
        
    except Exception as e:
        print(f"⚠️ Warning: Could not create examples sheet - {str(e)}")

def preview_kedb_inc_data(input_file):
    """Preview the KEDB_inc.xlsx data structure"""
    
    try:
        df = pd.read_excel(input_file)
        
        print(f"🔍 KEDB_inc.xlsx DATA PREVIEW:")
        print("=" * 60)
        print(f"Total rows: {len(df)}")
        print(f"Total columns: {len(df.columns)}")
        
        print(f"\nColumns found:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")
        
        # Check for required columns
        if 'KEDB' in df.columns and 'short_description' in df.columns:
            # KEDB analysis
            kedb_stats = df['KEDB'].value_counts()
            duplicates = kedb_stats[kedb_stats > 1]
            
            print(f"\n📊 KEDB Analysis:")
            print(f"  • Total entries: {len(df)}")
            print(f"  • Unique KEDB numbers: {df['KEDB'].nunique()}")
            print(f"  • KEDB numbers with multiple entries: {len(duplicates)}")
            
            # Show duplicate examples
            if len(duplicates) > 0:
                print(f"\n🔍 Top 5 KEDB numbers with most entries:")
                for kedb, count in duplicates.head().items():
                    print(f"    - {kedb}: {count} entries")
                
                # Show example of duplicates
                top_kedb = duplicates.index[0]
                example_descriptions = df[df['KEDB'] == top_kedb]['short_description'].dropna().tolist()
                print(f"\n📝 Example descriptions for KEDB '{top_kedb}':")
                for i, desc in enumerate(example_descriptions[:5], 1):
                    print(f"    {i}. {desc}")
                if len(example_descriptions) > 5:
                    print(f"    ... and {len(example_descriptions) - 5} more")
            
            print(f"\n📋 Sample data (first 3 rows):")
            sample_cols = ['KEDB', 'short_description'] + [col for col in df.columns if col not in ['KEDB', 'short_description']][:3]
            available_sample_cols = [col for col in sample_cols if col in df.columns]
            print(df[available_sample_cols].head(3).to_string(index=False, max_colwidth=50))
        
        else:
            missing_cols = []
            if 'KEDB' not in df.columns:
                missing_cols.append('KEDB')
            if 'short_description' not in df.columns:
                missing_cols.append('short_description')
            print(f"⚠️  Warning: Missing required columns: {missing_cols}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error previewing KEDB_inc.xlsx: {str(e)}")
        return False

# Main execution
if __name__ == "__main__":
    # File paths
    input_excel = "KEDB_inc.xlsx"
    output_excel = "KEDB_processed_unique_descriptions.xlsx"
    
    print("🚀 Starting KEDB_inc.xlsx Processing - Remove Duplicates & Combine Descriptions")
    print("=" * 80)
    
    # Check if input file exists
    if not os.path.exists(input_excel):
        print(f"❌ Error: {input_excel} not found!")
        print("Please ensure KEDB_inc.xlsx is in the current directory.")
        
        # Show available Excel files
        print(f"\n📁 Excel files in current directory:")
        excel_files = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xls'))]
        if excel_files:
            for file in excel_files:
                print(f"  - {file}")
        else:
            print("  No Excel files found.")
        exit(1)
    
    # Preview the data
    print("🔍 Analyzing KEDB_inc.xlsx structure...")
    if preview_kedb_inc_data(input_excel):
        
        # Ask for confirmation
        print(f"\n❓ Proceed with processing KEDB_inc.xlsx? (y/n): ", end="")
        confirmation = input().lower().strip()
        
        if confirmation in ['y', 'yes']:
            # Process the data
            processed_df, breakdown_df = process_kedb_inc_with_unique_descriptions(input_excel, output_excel)
            
            if processed_df is not None:
                print("\n" + "=" * 80)
                print("🎉 KEDB_inc.xlsx PROCESSING COMPLETE!")
                print(f"📊 Output file: {output_excel}")
                print(f"\n📋 Generated Sheets:")
                print(f"   1. 'Processed_KEDB_Data' - Main results with combined unique descriptions")
                print(f"   2. 'Original_Data' - Original KEDB_inc.xlsx data")
                print(f"   3. 'KEDB_Breakdown_Analysis' - Detailed breakdown per KEDB")
                print(f"   4. 'Summary_Statistics' - Overall processing statistics")
                print(f"   5. 'Before_After_Examples' - Examples showing duplicate removal")
                
                print(f"\n✅ Key Results:")
                if breakdown_df is not None:
                    kedbs_with_dups = len(breakdown_df[breakdown_df['has_duplicates'] == True])
                    print(f"   • Processed {len(processed_df)} unique KEDB numbers")
                    print(f"   • Cleaned duplicates from {kedbs_with_dups} KEDB numbers")
                    print(f"   • Combined descriptions using ' - ' separator")
        else:
            print("❌ Processing cancelled.")
    else:
        print("❌ Cannot proceed due to data analysis errors.")
