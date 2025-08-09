import re
from collections import Counter, defaultdict
import os

def find_repeated_text_patterns(input_file_path, output_file_path, min_occurrences=2):
    """
    Find and extract repeated text patterns from the cleaned file
    """
    
    try:
        # Read the cleaned file
        with open(input_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        lines = content.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        # Dictionary to store different types of repeated patterns
        repeated_patterns = {
            'exact_lines': [],
            'word_sequences': [],
            'phrases': [],
            'error_patterns': [],
            'partial_matches': []
        }
        
        print(f"📊 Analyzing {len(lines)} lines for repeated patterns...")
        
        # 1. Find exact repeated lines
        line_counts = Counter(lines)
        repeated_patterns['exact_lines'] = [
            (line, count) for line, count in line_counts.items() 
            if count >= min_occurrences
        ]
        
        # 2. Find repeated word sequences (2-5 words)
        word_sequences = defaultdict(int)
        for line in lines:
            words = line.split()
            for i in range(len(words)):
                for seq_len in range(2, min(6, len(words) - i + 1)):
                    sequence = ' '.join(words[i:i + seq_len])
                    if len(sequence) > 10:  # Only consider meaningful sequences
                        word_sequences[sequence] += 1
        
        repeated_patterns['word_sequences'] = [
            (seq, count) for seq, count in word_sequences.items() 
            if count >= min_occurrences
        ]
        
        # 3. Find repeated phrases using regex patterns
        phrase_patterns = [
            r'APPID[^\s]+',
            r'[A-Z_]+\[[^\]]+\]',
            r'BUSINESS_TRANSACTION[^\s]*',
            r'COLLECTION[^\s]*',
            r'DETECTED[^.]*',
            r'PROBLEM[^.]*',
            r'ERROR[^.]*',
            r'FAILED[^.]*'
        ]
        
        phrase_counts = defaultdict(int)
        for pattern in phrase_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                phrase_counts[match.strip()] += 1
        
        repeated_patterns['phrases'] = [
            (phrase, count) for phrase, count in phrase_counts.items() 
            if count >= min_occurrences and len(phrase) > 5
        ]
        
        # 4. Find error patterns specifically
        error_keywords = ['ERROR', 'FAILED', 'PROBLEM', 'VIOLATION', 'DETECTED']
        error_lines = []
        for line in lines:
            if any(keyword in line.upper() for keyword in error_keywords):
                error_lines.append(line)
        
        error_counts = Counter(error_lines)
        repeated_patterns['error_patterns'] = [
            (error, count) for error, count in error_counts.items() 
            if count >= min_occurrences
        ]
        
        # 5. Find partial matches (similar lines with small differences)
        partial_matches = defaultdict(list)
        for i, line1 in enumerate(lines):
            for j, line2 in enumerate(lines[i+1:], i+1):
                similarity = calculate_similarity(line1, line2)
                if 0.7 <= similarity < 1.0:  # 70-99% similar
                    key = min(line1, line2)  # Use lexicographically smaller as key
                    partial_matches[key].append((line1, line2, similarity))
        
        repeated_patterns['partial_matches'] = [
            (key, matches) for key, matches in partial_matches.items() 
            if len(matches) >= min_occurrences
        ]
        
        # Write results to output file
        write_repeated_patterns_to_file(repeated_patterns, output_file_path)
        
        print(f"✅ Repeated pattern analysis complete!")
        print(f"💾 Results saved to: {output_file_path}")
        
        return repeated_patterns
        
    except FileNotFoundError:
        print(f"❌ Error: Input file '{input_file_path}' not found.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def calculate_similarity(str1, str2):
    """Calculate similarity ratio between two strings"""
    from difflib import SequenceMatcher
    return SequenceMatcher(None, str1, str2).ratio()

def write_repeated_patterns_to_file(patterns, output_file):
    """Write all repeated patterns to output file"""
    
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("="*80 + "\n")
        file.write("           REPEATED TEXT PATTERNS ANALYSIS REPORT\n")
        file.write("="*80 + "\n\n")
        
        # 1. Exact repeated lines
        file.write("🔄 EXACT REPEATED LINES\n")
        file.write("-" * 40 + "\n")
        if patterns['exact_lines']:
            for line, count in sorted(patterns['exact_lines'], key=lambda x: x[1], reverse=True):
                file.write(f"Count: {count}\n")
                file.write(f"Text: {line}\n")
                file.write("-" * 40 + "\n")
        else:
            file.write("No exact repeated lines found.\n\n")
        
        # 2. Repeated word sequences
        file.write("\n🔤 REPEATED WORD SEQUENCES\n")
        file.write("-" * 40 + "\n")
        if patterns['word_sequences']:
            for sequence, count in sorted(patterns['word_sequences'], key=lambda x: x[1], reverse=True)[:20]:
                file.write(f"Count: {count}\n")
                file.write(f"Sequence: {sequence}\n")
                file.write("-" * 40 + "\n")
        else:
            file.write("No repeated word sequences found.\n\n")
        
        # 3. Repeated phrases
        file.write("\n📝 REPEATED PHRASES/PATTERNS\n")
        file.write("-" * 40 + "\n")
        if patterns['phrases']:
            for phrase, count in sorted(patterns['phrases'], key=lambda x: x[1], reverse=True):
                file.write(f"Count: {count}\n")
                file.write(f"Phrase: {phrase}\n")
                file.write("-" * 40 + "\n")
        else:
            file.write("No repeated phrases found.\n\n")
        
        # 4. Error patterns
        file.write("\n⚠️ REPEATED ERROR PATTERNS\n")
        file.write("-" * 40 + "\n")
        if patterns['error_patterns']:
            for error, count in sorted(patterns['error_patterns'], key=lambda x: x[1], reverse=True):
                file.write(f"Count: {count}\n")
                file.write(f"Error: {error}\n")
                file.write("-" * 40 + "\n")
        else:
            file.write("No repeated error patterns found.\n\n")
        
        # 5. Partial matches
        file.write("\n🔍 SIMILAR LINES (Partial Matches)\n")
        file.write("-" * 40 + "\n")
        if patterns['partial_matches']:
            for key, matches in list(patterns['partial_matches'].items())[:10]:
                file.write(f"Similar group (showing first few):\n")
                for line1, line2, similarity in matches[:3]:
                    file.write(f"Similarity: {similarity:.2%}\n")
                    file.write(f"Line 1: {line1}\n")
                    file.write(f"Line 2: {line2}\n")
                    file.write("-" * 20 + "\n")
                file.write("-" * 40 + "\n")
        else:
            file.write("No similar lines found.\n\n")

def create_summary_report(patterns, summary_file):
    """Create a summary report with statistics"""
    
    with open(summary_file, 'w', encoding='utf-8') as file:
        file.write("📊 REPEATED PATTERNS SUMMARY REPORT\n")
        file.write("="*50 + "\n\n")
        
        file.write(f"🔄 Exact repeated lines: {len(patterns['exact_lines'])}\n")
        file.write(f"🔤 Repeated word sequences: {len(patterns['word_sequences'])}\n")
        file.write(f"📝 Repeated phrases: {len(patterns['phrases'])}\n")
        file.write(f"⚠️ Repeated error patterns: {len(patterns['error_patterns'])}\n")
        file.write(f"🔍 Similar line groups: {len(patterns['partial_matches'])}\n\n")
        
        # Top repeated items
        if patterns['exact_lines']:
            top_repeated = sorted(patterns['exact_lines'], key=lambda x: x[1], reverse=True)[:5]
            file.write("🏆 TOP 5 MOST REPEATED LINES:\n")
            for i, (line, count) in enumerate(top_repeated, 1):
                file.write(f"{i}. ({count}x) {line[:100]}...\n")

# Main execution
if __name__ == "__main__":
    # File paths
    input_file = "output_advanced_clean.txt"  # Output from previous script
    output_file = "repeated_patterns_analysis.txt"
    summary_file = "repeated_patterns_summary.txt"
    
    print("🔍 Starting repeated pattern analysis...")
    print("=" * 60)
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ Error: '{input_file}' not found!")
        print("Make sure you've run the previous script first to generate the cleaned file.")
        exit(1)
    
    # Analyze repeated patterns
    patterns = find_repeated_text_patterns(input_file, output_file, min_occurrences=2)
    
    if patterns:
        # Create summary report
        create_summary_report(patterns, summary_file)
        print(f"📋 Summary report saved to: {summary_file}")
        
        print("\n" + "=" * 60)
        print("🎉 Repeated pattern analysis complete!")
        print(f"📄 Check '{output_file}' for detailed analysis")
        print(f"📋 Check '{summary_file}' for quick summary")
