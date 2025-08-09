import pandas as pd
import re
from collections import Counter
import os

def analyze_specific_issue_type(excel_file_path, text_file_path, target_issue_types, output_file_path):
    """
    Find matches between Excel short_description words and text file content
    for specific issue types only
    """
    
    try:
        # Read Excel file
        print("📊 Reading Excel file...")
        df = pd.read_excel(excel_file_path)
        
        # Check if required columns exist
        if 'short_description' not in df.columns or 'issue_type' not in df.columns:
            print("❌ Error: Excel file must contain 'short_description' and 'issue_type' columns")
            return None
        
        # Filter DataFrame for specific issue types
        if isinstance(target_issue_types, str):
            target_issue_types = [target_issue_types]
        
        filtered_df = df[df['issue_type'].isin(target_issue_types)]
        print(f"🎯 Filtered to {len(filtered_df)} records for issue types: {', '.join(target_issue_types)}")
        
        if filtered_df.empty:
            print("❌ No records found for the specified issue types!")
            return None
        
        # Read text file
        print("📄 Reading text file...")
        with open(text_file_path, 'r', encoding='utf-8') as file:
            text_content = file.read().lower()
        
        # Extract words from filtered short_description column
        print("🔍 Extracting words from filtered short descriptions...")
        all_description_words = []
        word_to_issue_type = {}
        
        for index, row in filtered_df.iterrows():
            if pd.notna(row['short_description']):
                description = str(row['short_description']).lower()
                issue_type = str(row['issue_type'])
                
                # Extract words (remove special characters, keep only alphanumeric)
                words = re.findall(r'\b[a-zA-Z0-9]+\b', description)
                
                for word in words:
                    if len(word) > 2:  # Only consider words with more than 2 characters
                        all_description_words.append(word)
                        
                        # Track issue types for this word
                        if word not in word_to_issue_type:
                            word_to_issue_type[word] = set()
                        word_to_issue_type[word].add(issue_type)
        
        print(f"📝 Found {len(set(all_description_words))} unique words in filtered descriptions")
        
        # Count occurrences of each word in text file
        print("🔎 Searching for word matches in text file...")
        word_matches = {}
        
        for word in set(all_description_words):
            # Count how many times this word appears in the text file
            pattern = r'\b' + re.escape(word) + r'\b'
            matches = len(re.findall(pattern, text_content, re.IGNORECASE))
            
            if matches > 0:
                word_matches[word] = {
                    'count_in_text': matches,
                    'count_in_descriptions': all_description_words.count(word),
                    'issue_types': list(word_to_issue_type[word])
                }
        
        # Sort by count in text file and get top 40
        sorted_matches = sorted(word_matches.items(), key=lambda x: x[1]['count_in_text'], reverse=True)
        top_40_matches = sorted_matches[:40]
        
        # Generate results
        results = {
            'target_issue_types': target_issue_types,
            'filtered_records': len(filtered_df),
            'total_unique_words': len(set(all_description_words)),
            'words_found_in_text': len(word_matches),
            'top_40_matches': top_40_matches
        }
        
        # Write results to file
        write_specific_results_to_file(results, output_file_path, excel_file_path, text_file_path)
        
        print(f"✅ Analysis complete for issue types: {', '.join(target_issue_types)}")
        print(f"📊 {len(word_matches)} words found in text file")
        print(f"💾 Results saved to: {output_file_path}")
        
        return results
        
    except FileNotFoundError as e:
        print(f"❌ Error: File not found - {str(e)}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def write_specific_results_to_file(results, output_file, excel_file, text_file):
    """Write analysis results for specific issue types to output file"""
    
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("="*80 + "\n")
        file.write("    SPECIFIC ISSUE TYPE - EXCEL WORDS vs TEXT FILE ANALYSIS\n")
        file.write("="*80 + "\n\n")
        
        file.write(f"📊 ANALYSIS SUMMARY:\n")
        file.write(f"Excel file: {excel_file}\n")
        file.write(f"Text file: {text_file}\n")
        file.write(f"Target issue types: {', '.join(results['target_issue_types'])}\n")
        file.write(f"Filtered records: {results['filtered_records']}\n")
        file.write(f"Total unique words in descriptions: {results['total_unique_words']}\n")
        file.write(f"Words found in text file: {results['words_found_in_text']}\n\n")
        
        file.write("🏆 TOP 40 MATCHING WORDS WITH COUNTS:\n")
        file.write("="*80 + "\n")
        file.write(f"{'Rank':<6} {'Word':<20} {'Text Count':<12} {'Desc Count':<12} {'Issue Types'}\n")
        file.write("-"*80 + "\n")
        
        for rank, (word, data) in enumerate(results['top_40_matches'], 1):
            issue_types_str = ', '.join(data['issue_types'])
            
            file.write(f"{rank:<6} {word:<20} {data['count_in_text']:<12} {data['count_in_descriptions']:<12} {issue_types_str}\n")

def get_available_issue_types(excel_file_path):
    """Get list of all available issue types in the Excel file"""
    
    try:
        df = pd.read_excel(excel_file_path)
        if 'issue_type' in df.columns:
            unique_issue_types = df['issue_type'].dropna().unique().tolist()
            return sorted(unique_issue_types)
        else:
            print("❌ 'issue_type' column not found in Excel file")
            return []
    except Exception as e:
        print(f"❌ Error reading Excel file: {str(e)}")
        return []

def interactive_issue_type_selection(excel_file_path):
    """Allow user to interactively select issue types"""
    
    available_types = get_available_issue_types(excel_file_path)
    
    if not available_types:
        return []
    
    print("\n📋 Available Issue Types:")
    print("=" * 40)
    for i, issue_type in enumerate(available_types, 1):
        print(f"{i:2d}. {issue_type}")
    
    print("\n🎯 Selection Options:")
    print("- Enter numbers separated by commas (e.g., 1,3,5)")
    print("- Enter 'all' to select all types")
    print("- Enter issue type names directly (e.g., Network,System)")
    
    selection = input("\nEnter your selection: ").strip()
    
    if selection.lower() == 'all':
        return available_types
    
    selected_types = []
    
    # Try to parse as numbers
    try:
        numbers = [int(x.strip()) for x in selection.split(',')]
        for num in numbers:
            if 1 <= num <= len(available_types):
                selected_types.append(available_types[num - 1])
            else:
                print(f"⚠️ Warning: Invalid selection {num}")
    except ValueError:
        # Try to parse as issue type names
        type_names = [x.strip() for x in selection.split(',')]
        for name in type_names:
            matching_types = [t for t in available_types if name.lower() in t.lower()]
            if matching_types:
                selected_types.extend(matching_types)
            else:
                print(f"⚠️ Warning: No match found for '{name}'")
    
    return list(set(selected_types))  # Remove duplicates

# Main execution
if __name__ == "__main__":
    # File paths - UPDATE THESE TO YOUR ACTUAL FILE PATHS
    excel_file = "your_excel_file.xlsx"  # Change this to your Excel file path
    text_file = "output_advanced_clean.txt"  # Or any text file you want to analyze
    
    print("🚀 Starting Specific Issue Type Analysis...")
    print("=" * 70)
    
    # Check if files exist
    if not os.path.exists(excel_file):
        print(f"❌ Error: Excel file '{excel_file}' not found!")
        print("Please update the 'excel_file' variable with the correct path.")
        exit(1)
    
    if not os.path.exists(text_file):
        print(f"❌ Error: Text file '{text_file}' not found!")
        print("Please update the 'text_file' variable with the correct path.")
        exit(1)
    
    # Method 1: Specify issue types directly in code
    # Uncomment and modify the line below to specify issue types directly:
    # target_issue_types = ["Network", "System", "Application"]  # Specify your target issue types here
    
    # Method 2: Interactive selection
    target_issue_types = interactive_issue_type_selection(excel_file)
    
    if not target_issue_types:
        print("❌ No issue types selected. Exiting...")
        exit(1)
    
    print(f"\n✅ Selected issue types: {', '.join(target_issue_types)}")
    
    # Generate output filename based on selected types
    safe_types = [t.replace(' ', '_').replace('/', '_') for t in target_issue_types]
    output_file = f"analysis_{'_'.join(safe_types[:3])}.txt"  # Use first 3 types in filename
    
    # Run analysis
    results = analyze_specific_issue_type(excel_file, text_file, target_issue_types, output_file)
    
    if results:
        # Print summary
        print("\n" + "=" * 70)
        print("📈 QUICK SUMMARY:")
        print(f"🎯 Issue types analyzed: {', '.join(target_issue_types)}")
        print(f"📄 Records filtered: {results['filtered_records']}")
        print(f"✅ Matching words found: {results['words_found_in_text']}")
        if results['top_40_matches']:
            print(f"🏆 Top word: '{results['top_40_matches'][0][0]}' with {results['top_40_matches'][0][1]['count_in_text']} matches")
        print(f"\n🎉 Analysis complete! Results saved to: {output_file}")
