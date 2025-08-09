import pandas as pd
import re
from collections import Counter
import os

def analyze_issue_type_word_frequency(excel_file_path, output_excel_path, min_word_length=3, min_count=2):
    """
    Analyze word frequency within each issue type's combined short descriptions
    and create a new Excel file with issue_type, word, and count columns
    """
    
    try:
        # Read Excel file
        print("📊 Reading Excel file...")
        df = pd.read_excel(excel_file_path)
        
        # Check if required columns exist
        if 'short_description' not in df.columns or 'issue_type' not in df.columns:
            print("❌ Error: Excel file must contain 'short_description' and 'issue_type' columns")
            return None
        
        # Remove rows with null values in required columns
        df_clean = df.dropna(subset=['short_description', 'issue_type'])
        print(f"📝 Processing {len(df_clean)} records with valid data")
        
        # Get unique issue types
        unique_issue_types = df_clean['issue_type'].unique()
        print(f"🎯 Found {len(unique_issue_types)} unique issue types")
        
        # Results list to store word frequency data
        results_data = []
        issue_type_stats = {}
        
        # Process each issue type
        for issue_type in unique_issue_types:
            print(f"\n🔍 Processing issue type: {issue_type}")
            
            # Filter data for current issue type
            issue_df = df_clean[df_clean['issue_type'] == issue_type]
            
            # Combine all short descriptions for this issue type
            combined_descriptions = ""
            for desc in issue_df['short_description']:
                combined_descriptions += " " + str(desc).lower()
            
            # Extract words from combined descriptions
            words = re.findall(r'\b[a-zA-Z0-9]+\b', combined_descriptions)
            
            # Filter words by minimum length
            filtered_words = [word for word in words if len(word) >= min_word_length]
            
            # Count word frequencies
            word_counts = Counter(filtered_words)
            
            # Filter by minimum count
            significant_words = {word: count for word, count in word_counts.items() if count >= min_count}
            
            # Store statistics
            issue_type_stats[issue_type] = {
                'total_descriptions': len(issue_df),
                'total_words': len(filtered_words),
                'unique_words': len(word_counts),
                'significant_words': len(significant_words)
            }
            
            # Add to results
            for word, count in significant_words.items():
                results_data.append({
                    'issue_type': issue_type,
                    'word': word,
                    'count': count,
                    'total_descriptions_in_type': len(issue_df),
                    'word_frequency_percentage': round((count / len(filtered_words)) * 100, 2)
                })
            
            print(f"   📄 Descriptions: {len(issue_df)}")
            print(f"   📝 Total words: {len(filtered_words)}")
            print(f"   🔤 Unique words: {len(word_counts)}")
            print(f"   ⭐ Significant words (≥{min_count}): {len(significant_words)}")
        
        # Create DataFrame from results
        results_df = pd.DataFrame(results_data)
        
        if results_df.empty:
            print("❌ No data generated. Try reducing min_word_length or min_count parameters.")
            return None
        
        # Sort by issue_type and count (descending)
        results_df = results_df.sort_values(['issue_type', 'count'], ascending=[True, False])
        
        # Create summary statistics sheet
        summary_data = []
        for issue_type, stats in issue_type_stats.items():
            summary_data.append({
                'issue_type': issue_type,
                'total_descriptions': stats['total_descriptions'],
                'total_words_analyzed': stats['total_words'],
                'unique_words_found': stats['unique_words'],
                'significant_words': stats['significant_words']
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df = summary_df.sort_values('total_descriptions', ascending=False)
        
        # Write to Excel with multiple sheets
        with pd.ExcelWriter(output_excel_path, engine='openpyxl') as writer:
            # Main results sheet
            results_df.to_excel(writer, sheet_name='Word_Frequency_Analysis', index=False)
            
            # Summary statistics sheet
            summary_df.to_excel(writer, sheet_name='Summary_Statistics', index=False)
            
            # Top words per issue type sheet
            create_top_words_sheet(results_df, writer)
        
        print(f"\n✅ Analysis complete!")
        print(f"📊 Total records processed: {len(results_data)}")
        print(f"💾 Results saved to: {output_excel_path}")
        
        # Print quick summary
        print(f"\n📈 QUICK SUMMARY:")
        for issue_type, stats in issue_type_stats.items():
            print(f"  {issue_type}: {stats['significant_words']} significant words from {stats['total_descriptions']} descriptions")
        
        return results_df, summary_df
        
    except FileNotFoundError:
        print(f"❌ Error: Excel file '{excel_file_path}' not found!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def create_top_words_sheet(results_df, writer):
    """Create a sheet showing top words for each issue type"""
    
    top_words_data = []
    
    for issue_type in results_df['issue_type'].unique():
        issue_data = results_df[results_df['issue_type'] == issue_type].head(20)  # Top 20 words
        
        for rank, (_, row) in enumerate(issue_data.iterrows(), 1):
            top_words_data.append({
                'issue_type': issue_type,
                'rank': rank,
                'word': row['word'],
                'count': row['count'],
                'frequency_percentage': row['word_frequency_percentage']
            })
    
    top_words_df = pd.DataFrame(top_words_data)
    top_words_df.to_excel(writer, sheet_name='Top_Words_Per_Type', index=False)

def create_detailed_analysis(excel_file_path, output_folder):
    """Create separate analysis files for advanced insights"""
    
    try:
        df = pd.read_excel(excel_file_path)
        df_clean = df.dropna(subset=['short_description', 'issue_type'])
        
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Analysis 1: Word length distribution
        word_length_analysis = []
        
        for issue_type in df_clean['issue_type'].unique():
            issue_df = df_clean[df_clean['issue_type'] == issue_type]
            combined_text = " ".join(issue_df['short_description'].astype(str))
            words = re.findall(r'\b[a-zA-Z0-9]+\b', combined_text.lower())
            
            length_counts = Counter(len(word) for word in words)
            
            for length, count in length_counts.items():
                word_length_analysis.append({
                    'issue_type': issue_type,
                    'word_length': length,
                    'count': count
                })
        
        length_df = pd.DataFrame(word_length_analysis)
        length_df.to_excel(f"{output_folder}/word_length_analysis.xlsx", index=False)
        
        # Analysis 2: Common words across issue types
        all_words = {}
        
        for issue_type in df_clean['issue_type'].unique():
            issue_df = df_clean[df_clean['issue_type'] == issue_type]
            combined_text = " ".join(issue_df['short_description'].astype(str))
            words = re.findall(r'\b[a-zA-Z0-9]+\b', combined_text.lower())
            word_counts = Counter(words)
            
            for word, count in word_counts.items():
                if len(word) >= 3:
                    if word not in all_words:
                        all_words[word] = {}
                    all_words[word][issue_type] = count
        
        # Find words that appear in multiple issue types
        common_words_data = []
        for word, issue_counts in all_words.items():
            if len(issue_counts) > 1:  # Word appears in multiple issue types
                total_count = sum(issue_counts.values())
                issue_types_list = list(issue_counts.keys())
                
                common_words_data.append({
                    'word': word,
                    'appears_in_types': len(issue_counts),
                    'total_count': total_count,
                    'issue_types': '; '.join(issue_types_list),
                    'individual_counts': '; '.join([f"{k}:{v}" for k, v in issue_counts.items()])
                })
        
        common_df = pd.DataFrame(common_words_data)
        common_df = common_df.sort_values('total_count', ascending=False)
        common_df.to_excel(f"{output_folder}/common_words_analysis.xlsx", index=False)
        
        print(f"📁 Additional analysis files saved to: {output_folder}/")
        
    except Exception as e:
        print(f"❌ Error in detailed analysis: {str(e)}")

def generate_word_cloud_data(results_df, output_csv_path):
    """Generate data suitable for word cloud visualization"""
    
    try:
        # Create word cloud data for each issue type
        wordcloud_data = []
        
        for issue_type in results_df['issue_type'].unique():
            issue_data = results_df[results_df['issue_type'] == issue_type]
            
            # Get top 50 words for this issue type
            top_words = issue_data.head(50)
            
            for _, row in top_words.iterrows():
                wordcloud_data.append({
                    'issue_type': issue_type,
                    'word': row['word'],
                    'count': row['count'],
                    'size_weight': min(100, row['count'] * 2)  # Weight for word cloud sizing
                })
        
        wordcloud_df = pd.DataFrame(wordcloud_data)
        wordcloud_df.to_csv(output_csv_path, index=False)
        print(f"☁️ Word cloud data saved to: {output_csv_path}")
        
    except Exception as e:
        print(f"❌ Error generating word cloud data: {str(e)}")

# Main execution
if __name__ == "__main__":
    # File paths - UPDATE THESE TO YOUR ACTUAL PATHS
    excel_file = "your_excel_file.xlsx"  # Change this to your Excel file path
    output_excel = "issue_type_word_frequency_analysis.xlsx"
    output_folder = "detailed_analysis"
    wordcloud_csv = "wordcloud_data.csv"
    
    print("🚀 Starting Issue Type Word Frequency Analysis...")
    print("=" * 80)
    
    # Check if input file exists
    if not os.path.exists(excel_file):
        print(f"❌ Error: Excel file '{excel_file}' not found!")
        print("Please update the 'excel_file' variable with the correct path.")
        
        # Show current directory files for reference
        print(f"\n📁 Files in current directory:")
        for file in os.listdir('.'):
            if file.endswith(('.xlsx', '.xls')):
                print(f"  - {file}")
        exit(1)
    
    # Parameters for analysis
    MIN_WORD_LENGTH = 3  # Minimum word length to consider
    MIN_COUNT = 2        # Minimum count for a word to be included
    
    print(f"⚙️ Analysis parameters:")
    print(f"   - Minimum word length: {MIN_WORD_LENGTH}")
    print(f"   - Minimum word count: {MIN_COUNT}")
    
    # Main analysis
    results_df, summary_df = analyze_issue_type_word_frequency(
        excel_file, 
        output_excel, 
        min_word_length=MIN_WORD_LENGTH, 
        min_count=MIN_COUNT
    )
    
    if results_df is not None:
        # Generate additional analysis files
        print(f"\n🔬 Creating detailed analysis...")
        create_detailed_analysis(excel_file, output_folder)
        
        # Generate word cloud data
        print(f"\n☁️ Generating word cloud data...")
        generate_word_cloud_data(results_df, wordcloud_csv)
        
        print("\n" + "=" * 80)
        print("🎉 Analysis Complete!")
        print(f"📊 Main results: {output_excel}")
        print(f"📁 Detailed analysis: {output_folder}/")
        print(f"☁️ Word cloud data: {wordcloud_csv}")
        
        # Show sample of results
        print(f"\n📋 Sample Results:")
        print(results_df.head(10).to_string(index=False))
