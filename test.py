import re
import string

def extract_unique_words(input_file, output_file):
    """
    Extract unique words from input file and write them to output file
    
    Args:
        input_file (str): Path to the input text file
        output_file (str): Path to the output text file
    """
    
    try:
        # Read the input file
        with open(input_file, 'r', encoding='utf-8') as file:
            text = file.read()
        
        # Convert to lowercase for case-insensitive comparison
        text = text.lower()
        
        # Remove punctuation and split into words
        # Using regex to extract only alphabetic words
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        
        # Alternative method using string operations:
        # translator = str.maketrans('', '', string.punctuation)
        # text = text.translate(translator)
        # words = text.split()
        
        # Get unique words using set
        unique_words = set(words)
        
        # Sort the unique words alphabetically (optional)
        unique_words_sorted = sorted(unique_words)
        
        # Write unique words to output file
        with open(output_file, 'w', encoding='utf-8') as file:
            for word in unique_words_sorted:
                file.write(word + '\n')
        
        print(f"Successfully extracted {len(unique_words)} unique words")
        print(f"Unique words saved to: {output_file}")
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    # Specify input and output file paths
    input_file = "input.txt"  # Change this to your input file path
    output_file = "unique_words.txt"  # Change this to your desired output file path
    
    # Call the function
    extract_unique_words(input_file, output_file)
    
    # Optional: Display some statistics
    try:
        with open(output_file, 'r', encoding='utf-8') as file:
            unique_words = file.read().strip().split('\n')
            print(f"\nFirst 10 unique words:")
            for i, word in enumerate(unique_words[:10], 1):
                print(f"{i}. {word}")
            
            if len(unique_words) > 10:
                print(f"... and {len(unique_words) - 10} more words")
                
    except FileNotFoundError:
        pass

if __name__ == "__main__":
    main()
