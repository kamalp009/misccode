import re
from collections import OrderedDict

def clean_and_extract_unique_data(input_file_path, output_file_path):
    """
    Extract unique data from a text file by removing repeated words and duplicate lines
    """
    
    try:
        # Read the input file
        with open(input_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Split content into lines
        lines = content.split('\n')
        
        # Method 1: Remove duplicate lines while preserving order
        unique_lines = list(OrderedDict.fromkeys(lines))
        
        # Method 2: For each line, remove repeated words
        processed_lines = []
        
        for line in unique_lines:
            if line.strip():  # Skip empty lines
                # Split line into words
                words = line.split()
                
                # Remove repeated words while preserving order
                unique_words = list(OrderedDict.fromkeys(words))
                
                # Join words back into a line
                processed_line = ' '.join(unique_words)
                processed_lines.append(processed_line)
        
        # Write to output file
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write('\n'.join(processed_lines))
        
        print(f"✅ Processing complete!")
        print(f"📄 Original lines: {len(lines)}")
        print(f"📄 Unique lines: {len(processed_lines)}")
        print(f"💾 Output saved to: {output_file_path}")
        
        return processed_lines
        
    except FileNotFoundError:
        print(f"❌ Error: Input file '{input_file_path}' not found.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def extract_specific_patterns(input_file_path, output_file_path):
    """
    Extract specific patterns like error codes, timestamps, etc.
    """
    
    try:
        with open(input_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Define patterns to extract
        patterns = {
            'error_codes': r'[A-Z_]+\[[^\]]+\]',
            'timestamps': r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
            'ip_addresses': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
            'application_names': r'APPID[^\s]+',
            'transaction_types': r'BUSINESS_TRANSACTION|COLLECTION|ACCOUNTSEARCH',
        }
        
        extracted_data = {}
        
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, content)
            # Remove duplicates while preserving order
            unique_matches = list(OrderedDict.fromkeys(matches))
            extracted_data[pattern_name] = unique_matches
        
        # Write extracted data to file
        with open(output_file_path, 'w', encoding='utf-8') as file:
            for pattern_name, matches in extracted_data.items():
                file.write(f"\n=== {pattern_name.upper().replace('_', ' ')} ===\n")
                for match in matches:
                    file.write(f"{match}\n")
        
        print(f"✅ Pattern extraction complete!")
        print(f"💾 Extracted data saved to: {output_file_path}")
        
        return extracted_data
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def advanced_text_cleaning(input_file_path, output_file_path):
    """
    Advanced cleaning with multiple options
    """
    
    try:
        with open(input_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Clean the text
        lines = content.split('\n')
        cleaned_lines = []
        seen_lines = set()
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
            
            # Convert to lowercase for comparison (optional)
            line_lower = line.lower().strip()
            
            # Skip if we've seen this line before
            if line_lower in seen_lines:
                continue
            
            seen_lines.add(line_lower)
            
            # Clean individual words in the line
            words = line.split()
            seen_words = set()
            unique_words = []
            
            for word in words:
                word_clean = word.lower()
                if word_clean not in seen_words:
                    seen_words.add(word_clean)
                    unique_words.append(word)
            
            cleaned_line = ' '.join(unique_words)
            cleaned_lines.append(cleaned_line)
        
        # Write cleaned content
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write('\n'.join(cleaned_lines))
        
        print(f"✅ Advanced cleaning complete!")
        print(f"📄 Original lines: {len(lines)}")
        print(f"📄 Cleaned unique lines: {len(cleaned_lines)}")
        print(f"💾 Output saved to: {output_file_path}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

# Main execution
if __name__ == "__main__":
    # File paths
    input_file = "input.txt"  # Change this to your input file path
    output_file_unique = "output_unique.txt"
    output_file_patterns = "output_patterns.txt"
    output_file_advanced = "output_advanced_clean.txt"
    
    print("🚀 Starting text processing...")
    print("=" * 50)
    
    # Option 1: Basic unique line and word extraction
    print("\n1️⃣ Basic unique data extraction:")
    clean_and_extract_unique_data(input_file, output_file_unique)
    
    # Option 2: Extract specific patterns
    print("\n2️⃣ Pattern-based extraction:")
    extract_specific_patterns(input_file, output_file_patterns)
    
    # Option 3: Advanced cleaning
    print("\n3️⃣ Advanced text cleaning:")
    advanced_text_cleaning(input_file, output_file_advanced)
    
    print("\n" + "=" * 50)
    print("🎉 All processing complete!")
