import pandas as pd
import re
from tqdm import tqdm

def is_quality_english(text, min_words=4, min_alpha_ratio=0.5, min_length=15):
    """
    Check if text appears to be quality English using improved heuristics:
    - Has sufficient number of words
    - Contains a good ratio of alphabetic characters
    - Is long enough to be meaningful
    - Contains multiple common English words or patterns
    - Avoids texts with too many placeholders or non-text patterns
    """
    if pd.isna(text) or not isinstance(text, str) or text.strip() == '':
        return False
    
    # Clean the text
    cleaned_text = re.sub(r'\s+', ' ', str(text)).strip()
    
    # Check minimum length requirement
    if len(cleaned_text) < min_length:
        return False
        
    # Check for too many sequential X characters (likely placeholders)
    if re.search(r'X{5,}', cleaned_text):
        # Texts with too many placeholder Xs are less useful
        return False
        
    # Count words
    words = cleaned_text.split()
    if len(words) < min_words:
        return False
        
    # Check ratio of alphabetic characters to total length
    alpha_chars = sum(c.isalpha() for c in cleaned_text)
    if len(cleaned_text) > 0 and alpha_chars / len(cleaned_text) < min_alpha_ratio:
        return False
    
    # Check for common English words (improved list)
    common_english_words = [
        'the', 'and', 'for', 'you', 'are', 'your', 'will', 'have', 'from', 
        'this', 'with', 'that', 'send', 'please', 'money', 'bank', 'account', 
        'contact', 'code', 'number', 'phone', 'call', 'cash', 'credit', 'payment',
        'free', 'claim', 'prize', 'win', 'won', 'congratulations', 'urgent'
    ]
    lower_text = cleaned_text.lower()
    
    # Count how many common English words appear
    english_word_count = sum(1 for word in common_english_words if f" {word} " in f" {lower_text} ")
    
    # Require at least 2 common English words for longer texts, 1 for shorter texts
    if len(cleaned_text) > 50:
        return english_word_count >= 2
    else:
        return english_word_count >= 1

def extract_quality_english_text(input_file, output_file, text_columns=None):
    """Extract higher quality English text from a CSV into a single column."""
    # Load data
    print(f"Loading CSV from {input_file}...")
    
    try:
        # Try to read with default settings first
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error with standard CSV parsing: {e}")
        print("Trying alternative parsing methods...")
        try:
            # Try with different encoding
            df = pd.read_csv(input_file, encoding='latin1')
        except Exception:
            # Last resort - try with most flexible settings
            df = pd.read_csv(input_file, encoding='utf-8', engine='python', on_bad_lines='skip')
    
    total_rows = len(df)
    print(f"Loaded {total_rows} rows")
    
    # If no specific text columns are provided, use all columns
    if text_columns is None or not all(col in df.columns for col in text_columns):
        text_columns = df.columns
        print(f"Checking all {len(text_columns)} columns for quality English text")
    
    # Extract potential English text from all specified columns
    all_texts = []
    
    for _, row in tqdm(df.iterrows(), total=total_rows, desc="Processing rows"):
        row_texts = []
        
        # Check each column in the row
        for col in text_columns:
            cell_text = str(row[col]) if not pd.isna(row[col]) else ""
            
            # Skip obviously non-text values
            if cell_text.strip() in ["", "nan", "None", "0", "NaN"]:
                continue
                
            # If cell appears to contain quality English text, add it
            if is_quality_english(cell_text):
                row_texts.append(cell_text)
        
        # If we found any quality English text in this row, add the longest one
        if row_texts:
            # Sort by length and take the longest text
            longest_text = sorted(row_texts, key=len, reverse=True)[0]
            all_texts.append(longest_text)
    
    # Create a new DataFrame with just one column of the extracted text
    result_df = pd.DataFrame({"english_text": all_texts})
    
    # Remove any duplicate texts
    result_df.drop_duplicates(inplace=True)
    
    # Save the filtered data
    result_df.to_csv(output_file, index=False)
    
    print(f"Extraction complete!")
    print(f"Extracted {len(result_df)} unique quality English texts ({len(result_df)/total_rows:.1%} of original rows)")
    print(f"Results saved to {output_file}")
    
    return result_df

if __name__ == "__main__":
    # ========== CONFIGURATION SECTION ==========
    # MODIFY THESE VALUES:
    
    # Input file path
    INPUT_FILE = r"C:/Users/Ahed/Desktop/THESIS/Test/tweet_sms_2018-01.csv"  
    
    # Output file path
    OUTPUT_FILE = r"C:/Users/Ahed/Desktop/THESIS/Test/quality_english_texts.csv"  
    
    # Columns to check for English text (None = check all columns)
    TEXT_COLUMNS = None  # Will check all columns
    
    # ==========================================
    
    # Run the extraction function
    extract_quality_english_text(INPUT_FILE, OUTPUT_FILE, TEXT_COLUMNS)