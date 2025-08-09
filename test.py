import pandas as pd
import re
from collections import Counter
import os

def analyze_issue_type_word_frequency_with_unique(excel_file_path, output_excel_path, unique_words_excel_path, min_word_length=3, min_count=2):
    """
    Analyze word frequency within each issue type's combined short descriptions
    and create Excel files including unique words that appear only in specific issue types
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
        
        # Dictionary to store all words for each issue type
        issue_type_words = {}
        
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
            
            # Store words for this issue type (for unique word analysis)
            issue_type_words[issue_type] = set(significant_words.keys())
            
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
        
        # Find unique words for each issue type
        print(f"\n🔍 Finding unique words for each issue type...")
        unique_words_data = find_unique_words_per_issue_type(issue_type_words, results_data)
        
        # Create DataFrame from results
        results_df = pd.DataFrame(results_data)
        unique_words_df = pd.DataFrame(unique_words_data)
        
        if results_df.empty:
            print("❌ No data generated. Try reducing min_word_length or min_count parameters.")
            return None
        
        # Sort by issue_type and count (descending)
        results_df = results_df.sort_values(['issue_type', 'count'], ascending=[True, False])
        unique_words_df = unique_words_df.sort_values(['issue_type', 'count'], ascending=[True, False])
        
        # Create summary statistics sheet
        summary_data = []
        for issue_type, stats in issue_type_stats.items():
            unique_count = len(unique_words_df[unique_words_df['issue_type'] == issue_type])
            summary_data.append({
                'issue_type': issue_type,
                'total_descriptions': stats['total_descriptions'],
                'total_words_analyzed': stats['total_words'],
                'unique_words_found': stats['unique_words'],
                'significant_words': stats['significant_words'],
                'unique_to_this_type': unique_count
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df = summary_df.sort_values('total_descriptions', ascending=False)
        
        # Write main analysis to Excel with multiple sheets
        with pd.ExcelWriter(output_excel_path, engine='openpyxl') as writer:
            # Main results sheet
            results_df.to_excel(writer, sheet_name='Word_Frequency_Analysis', index=False)
            
            # Summary statistics sheet
            summary_df.to_excel(writer, sheet_name='Summary_Statistics', index=False)
            
            # Top words per issue type sheet
            create_top_words_sheet(results_df, writer)
        
        # Write unique words analysis to separate Excel file
        with pd.ExcelWriter(unique_words_excel_path, engine='openpyxl') as writer:
            # Unique words main sheet
            unique_words_df.to_excel(writer, sheet_name='Unique_Words_Per_Type', index=False)
            
            # Create comparison matrix sheet
            create_word_comparison_matrix(issue_type_words, writer)
            
            # Create unique words summary
            create_unique_words_summary(unique_words_df, writer)
        
        print(f"\n✅ Analysis complete!")
        print(f"📊 Total records processed: {len(results_data)}")
        print(f"🔍 Unique words found: {len(unique_words_data)}")
        print(f"💾 Main results saved to: {output_excel_path}")
        print(f"💾 Unique words analysis saved to: {unique_words_excel_path}")
        
        # Print quick summary
        print(f"\n📈 QUICK SUMMARY:")
        for issue_type, stats in issue_type_stats.items():
            unique_count = len(unique_words_df[unique_words_df['issue_type'] == issue_type])
            print(f"  {issue_type}: {stats['significant_words']} total words, {unique_count} unique words")
        
        return results_df, unique_words_df, summary_df
        
    except FileNotFoundError:
        print(f"❌ Error: Excel file '{excel_file_path}' not found!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def find_unique_words_per_issue_type(issue_type_words, results_data):
    """
    Find words that appear in one issue type but not in others
    """
    
    unique_words_data = []
    
    # Create a dictionary for quick lookup of word counts
    word_count_lookup = {}
    for item in results_data:
        key = (item['issue_type'], item['word'])
        word_count_lookup[key] = item
    
    # Check each issue type's words against all other issue types
    for current_issue_type, current_words in issue_type_words.items():
        other_issue_types = [it for it in issue_type_words.keys() if it != current_issue_type]
        
        # Get all words from other issue types
        other_words = set()
        for other_type in other_issue_types:
            other_words.update(issue_type_words[other_type])
        
        # Find words that are in current type but not in any other type
        unique_words = current_words - other_words
        
        # Add unique words with their counts to results
        for word in unique_words:
            key = (current_issue_type, word)
            if key in word_count_lookup:
                word_data = word_count_lookup[key]
                unique_words_data.append({
                    'issue_type': current_issue_type,
                    'word': word,
                    'count': word_data['count'],
                    'word_frequency_percentage': word_data['word_frequency_percentage'],
                    'total_descriptions_in_type': word_data['total_descriptions_in_type'],
                    'uniqueness_score': calculate_uniqueness_score(word, current_issue_type, issue_type_words)
                })
    
    return unique_words_data

def calculate_uniqueness_score(word, issue_type, issue_type_words):
    """
    Calculate a uniqueness score based on how many issue types contain this word
    Score = 100 means completely unique to one type
    """
    
    appearances = 0
    for it_type, words in issue_type_words.items():
        if word in words:
            appearances += 1
    
    # Higher score for more unique words
    uniqueness_score = round(100 / appearances, 2)
    return uniqueness_score

def create_word_comparison_matrix(issue_type_words, writer):
    """
    Create a matrix showing word overlap between issue types
    """
    
    issue_types = list(issue_type_words.keys())
    matrix_data = []
    
    for type1 in issue_types:
        row = {'issue_type': type1}
        for type2 in issue_types:
            if type1 == type2:
                row[type2] = len(issue_type_words[type1])  # Total words in same type
            else:
                # Count common words between type1 and type2
                common_words = len(issue_type_words[type1] & issue_type_words[type2])
                row[type2] = common_words
        matrix_data.append(row)
    
    matrix_df = pd.DataFrame(matrix_data)
    matrix_df.to_excel(writer, sheet_name='Word_Overlap_Matrix', index=False)

def create_unique_words_summary(unique_words_df, writer):
    """
    Create a summary sheet for unique words analysis
    """
    
    summary_data = []
    
    for issue_type in unique_words_df['issue_type'].unique():
        type_data = unique_words_df[unique_words_df['issue_type'] == issue_type]
        
        summary_data.append({
            'issue_type': issue_type,
            'total_unique_words': len(type_data),
            'avg_word_count': round(type_data['count'].mean(), 2),
            'max_word_count': type_data['count'].max(),
            'top_unique_word': type_data.iloc[0]['word'] if len(type_data) > 0 else '',
            'top_word_count': type_data.iloc[0]['count'] if len(type_data) > 0 else 0
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df = summary_df.sort_values('total_unique_words', ascending=False)
    summary_df.to_excel(writer, sheet_name='Unique_Words_Summary', index=False)

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

def create_cross_type_analysis(unique_words_df, output_folder):
    """
    Create additional analysis files for cross-type comparison
    """
    
    try:
        os.makedirs(output_folder, exist_ok=True)
        
        # Analysis 1: Issue types with most unique words
        type_unique_counts = unique_words_df.groupby('issue_type').size().reset_index(name='unique_word_count')
        type_unique_counts = type_unique_counts.sort_values('unique_word_count', ascending=False)
        type_unique_counts.to_excel(f"{output_folder}/issue_types_by_uniqueness.xlsx", index=False)
        
        # Analysis 2: High-frequency unique words
        high_freq_unique = unique_words_df[unique_words_df['count'] >= 5].copy()
        high_freq_unique = high_freq_unique.sort_values(['count', 'uniqueness_score'], ascending=[False, False])
        high_freq_unique.to_excel(f"{output_folder}/high_frequency_unique_words.xlsx", index=False)
        
        print(f"📁 Cross-type analysis files saved to: {output_folder}/")
        
    except Exception as e:
        print(f"❌ Error in cross-type analysis: {str(e)}")

# Main execution
if __name__ == "__main__":
    # File paths - UPDATE THESE TO YOUR ACTUAL PATHS
    excel_file = "your_excel_file.xlsx"  # Change this to your Excel file path
    output_excel = "issue_type_word_frequency_analysis.xlsx"
    unique_words_excel = "unique_words_per_issue_type.xlsx"
    output_folder = "cross_type_analysis"
    
    print("🚀 Starting Enhanced Issue Type Word Frequency Analysis...")
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
    results_df, unique_words_df, summary_df = analyze_issue_type_word_frequency_with_unique(
        excel_file, 
        output_excel, 
        unique_words_excel,
        min_word_length=MIN_WORD_LENGTH, 
        min_count=MIN_COUNT
    )
    
    if results_df is not None and unique_words_df is not None:
        # Generate cross-type analysis
        print(f"\n🔬 Creating cross-type analysis...")
        create_cross_type_analysis(unique_words_df, output_folder)
        
        print("\n" + "=" * 80)
        print("🎉 Enhanced Analysis Complete!")
        print(f"📊 Main word frequency results: {output_excel}")
        print(f"🔍 Unique words analysis: {unique_words_excel}")
        print(f"📁 Cross-type analysis: {output_folder}/")
        
        # Show sample of unique words results
        print(f"\n🔍 Sample Unique Words Results:")
        if len(unique_words_df) > 0:
            print(unique_words_df.head(10).to_string(index=False))
        else:
            print("No unique words found with current parameters. Try reducing min_count.")
        
        # Show summary statistics
        print(f"\n📈 Unique Words Summary by Issue Type:")
        type_summary = unique_words_df.groupby('issue_type').agg({
            'word': 'count',
            'count': ['mean', 'max'],
            'uniqueness_score': 'mean'
        }).round(2)
        print(type_summary.to_string())
