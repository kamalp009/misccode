import pandas as pd
import re
from collections import defaultdict
import os

def process_resolution_data_and_generate_prompts(sheet1_path, excel2_path, output_file):
    """
    Read data from two Excel files, match KEDB with servicenow_id,
    combine resolution data by issue type, and generate AI prompts
    """
    
    try:
        # Read both Excel files
        print("📊 Reading Excel files...")
        
        # Read sheet1.xlsx - contains KEDB and issue_type columns
        sheet1_df = pd.read_excel(sheet1_path)
        print(f"📄 Sheet1 loaded: {len(sheet1_df)} records")
        
        # Read excel2.xlsx - contains servicenow_id and resolution columns
        excel2_df = pd.read_excel(excel2_path)
        print(f"📄 Excel2 loaded: {len(excel2_df)} records")
        
        # Validate required columns
        required_sheet1_cols = ['KEDB', 'issue_type']
        required_excel2_cols = ['servicenow_id', 'resolution']
        
        # Check if short_description exists in sheet1 (for prompt generation)
        if 'short_description' in sheet1_df.columns:
            required_sheet1_cols.append('short_description')
            has_short_description = True
        else:
            has_short_description = False
            print("⚠️ Warning: 'short_description' column not found in sheet1. Will generate generic prompts.")
        
        for col in required_sheet1_cols:
            if col not in sheet1_df.columns:
                print(f"❌ Error: Column '{col}' not found in sheet1.xlsx")
                return None
        
        for col in required_excel2_cols:
            if col not in excel2_df.columns:
                print(f"❌ Error: Column '{col}' not found in excel2.xlsx")
                return None
        
        # Clean data - remove nulls and convert to string for matching
        sheet1_clean = sheet1_df.dropna(subset=['KEDB', 'issue_type']).copy()
        excel2_clean = excel2_df.dropna(subset=['servicenow_id', 'resolution']).copy()
        
        # Convert KEDB and servicenow_id to string for matching
        sheet1_clean['KEDB'] = sheet1_clean['KEDB'].astype(str).str.strip()
        excel2_clean['servicenow_id'] = excel2_clean['servicenow_id'].astype(str).str.strip()
        
        print(f"🔍 Matching KEDB with servicenow_id...")
        
        # Merge the dataframes based on KEDB = servicenow_id
        merged_df = pd.merge(
            sheet1_clean, 
            excel2_clean, 
            left_on='KEDB', 
            right_on='servicenow_id', 
            how='inner'
        )
        
        print(f"✅ Found {len(merged_df)} matching records")
        
        if merged_df.empty:
            print("❌ No matching records found between KEDB and servicenow_id")
            return None
        
        # Group by issue_type and combine resolution data
        print(f"📋 Combining resolution data by issue type...")
        
        issue_type_resolutions = defaultdict(list)
        issue_type_descriptions = defaultdict(list)
        
        for _, row in merged_df.iterrows():
            issue_type = row['issue_type']
            resolution = str(row['resolution']).strip()
            
            if resolution and resolution.lower() not in ['nan', 'none', '']:
                issue_type_resolutions[issue_type].append(resolution)
            
            if has_short_description and pd.notna(row['short_description']):
                description = str(row['short_description']).strip()
                if description and description.lower() not in ['nan', 'none', '']:
                    issue_type_descriptions[issue_type].append(description)
        
        # Generate combined resolution data and prompts
        prompt_data = []
        
        for issue_type, resolutions in issue_type_resolutions.items():
            # Combine all resolutions for this issue type
            combined_resolutions = "\n".join([f"• {res}" for res in resolutions])
            
            # Get sample descriptions if available
            sample_descriptions = ""
            if issue_type in issue_type_descriptions:
                descriptions = list(set(issue_type_descriptions[issue_type]))[:5]  # Get unique, limit to 5
                sample_descriptions = "\n".join([f"- {desc}" for desc in descriptions])
            
            # Generate AI prompt for this issue type
            ai_prompt = generate_resolution_prompt(issue_type, combined_resolutions, sample_descriptions, has_short_description)
            
            prompt_data.append({
                'issue_type': issue_type,
                'total_resolutions': len(resolutions),
                'unique_resolutions': len(set(resolutions)),
                'combined_resolution_steps': combined_resolutions,
                'sample_descriptions': sample_descriptions if sample_descriptions else 'N/A',
                'ai_prompt_for_resolution_generation': ai_prompt
            })
        
        # Create DataFrame and save to Excel
        prompt_df = pd.DataFrame(prompt_data)
        prompt_df = prompt_df.sort_values('total_resolutions', ascending=False)
        
        # Save to Excel with multiple sheets
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Main prompts sheet
            prompt_df.to_excel(writer, sheet_name='Resolution_Prompts', index=False)
            
            # Detailed matching data
            merged_df.to_excel(writer, sheet_name='Matched_Data', index=False)
            
            # Summary statistics
            create_resolution_summary(prompt_df, writer)
        
        print(f"\n✅ Processing complete!")
        print(f"📊 Processed {len(issue_type_resolutions)} issue types")
        print(f"💾 Prompts and data saved to: {output_file}")
        
        # Display sample prompts
        display_sample_prompts(prompt_df)
        
        return prompt_df
        
    except FileNotFoundError as e:
        print(f"❌ Error: File not found - {str(e)}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def generate_resolution_prompt(issue_type, combined_resolutions, sample_descriptions, has_descriptions):
    """
    Generate AI prompt for creating resolution steps based on combined data
    """
    
    if has_descriptions and sample_descriptions:
        prompt = f"""You are an expert IT support specialist. Based on the following data for "{issue_type}" issues, generate step-by-step resolution instructions for new similar problems.

**Issue Type:** {issue_type}

**Historical Resolution Steps:**
{combined_resolutions}

**Sample Problem Descriptions:**
{sample_descriptions}

**Task:** When given a new short description for a "{issue_type}" issue, analyze it and provide:

1. **Root Cause Analysis:** Identify the likely cause based on the description
2. **Step-by-Step Resolution:** Provide detailed resolution steps based on historical successful resolutions
3. **Prerequisites:** List any prerequisites or permissions needed
4. **Expected Outcome:** What the user should expect after following the steps
5. **Alternative Solutions:** If primary solution doesn't work, suggest alternatives
6. **Prevention:** Recommend steps to prevent this issue in the future

**Output Format:**
- Use clear, numbered steps
- Include specific commands, settings, or actions where applicable
- Mention estimated time for resolution
- Include any warnings or cautions

**Example Usage:**
Input: "New {issue_type} problem description here"
Output: Structured resolution steps following the above format."""

    else:
        prompt = f"""You are an expert IT support specialist. Based on the following historical resolution data for "{issue_type}" issues, generate step-by-step resolution instructions for new similar problems.

**Issue Type:** {issue_type}

**Historical Resolution Steps:**
{combined_resolutions}

**Task:** When given a new problem description related to "{issue_type}" issues, provide:

1. **Problem Analysis:** Analyze the description and categorize the issue
2. **Step-by-Step Resolution:** Provide detailed resolution steps based on historical successful resolutions above
3. **Prerequisites:** List any prerequisites or permissions needed
4. **Expected Outcome:** What should happen after following the steps
5. **Troubleshooting:** Additional steps if the primary solution doesn't work
6. **Best Practices:** Recommendations to prevent similar issues

**Output Format:**
- Use clear, numbered steps
- Include specific technical details where applicable
- Mention estimated resolution time
- Include any important warnings

**Example Usage:**
Input: "Problem description for {issue_type} issue"
Output: Comprehensive resolution guide following the above structure."""

    return prompt

def create_resolution_summary(prompt_df, writer):
    """Create summary statistics sheet"""
    
    summary_data = []
    total_resolutions = prompt_df['total_resolutions'].sum()
    
    for _, row in prompt_df.iterrows():
        summary_data.append({
            'issue_type': row['issue_type'],
            'total_resolutions': row['total_resolutions'],
            'unique_resolutions': row['unique_resolutions'],
            'resolution_diversity': round((row['unique_resolutions'] / row['total_resolutions']) * 100, 2) if row['total_resolutions'] > 0 else 0,
            'percentage_of_total': round((row['total_resolutions'] / total_resolutions) * 100, 2)
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_excel(writer, sheet_name='Summary_Statistics', index=False)

def display_sample_prompts(prompt_df):
    """Display sample prompts for verification"""
    
    print(f"\n🤖 SAMPLE AI PROMPTS GENERATED:")
    print("=" * 80)
    
    # Show top 3 issue types by resolution count
    top_3 = prompt_df.head(3)
    
    for i, (_, row) in enumerate(top_3.iterrows(), 1):
        print(f"\n{i}. ISSUE TYPE: {row['issue_type']}")
        print(f"   Resolutions: {row['total_resolutions']} (Unique: {row['unique_resolutions']})")
        print(f"   Prompt Preview:")
        # Show first 300 characters of the prompt
        prompt_preview = row['ai_prompt_for_resolution_generation'][:300] + "..."
        print(f"   {prompt_preview}")
        print("-" * 60)

def create_individual_prompt_files(prompt_df, output_folder):
    """Create individual prompt files for each issue type"""
    
    try:
        os.makedirs(output_folder, exist_ok=True)
        
        for _, row in prompt_df.iterrows():
            issue_type = row['issue_type']
            safe_filename = re.sub(r'[^\w\-_.]', '_', issue_type)
            
            filename = f"{output_folder}/prompt_{safe_filename}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"AI RESOLUTION PROMPT FOR: {issue_type}\n")
                f.write("=" * 60 + "\n\n")
                f.write(row['ai_prompt_for_resolution_generation'])
                f.write(f"\n\n--- STATISTICS ---\n")
                f.write(f"Total Resolutions: {row['total_resolutions']}\n")
                f.write(f"Unique Resolutions: {row['unique_resolutions']}\n")
        
        print(f"📁 Individual prompt files saved to: {output_folder}/")
        
    except Exception as e:
        print(f"❌ Error creating individual files: {str(e)}")

# Main execution
if __name__ == "__main__":
    # File paths - UPDATE THESE TO YOUR ACTUAL PATHS
    sheet1_file = "shee1.xlsx"        # Contains KEDB and issue_type columns
    excel2_file = "excel2.xlsx"       # Contains servicenow_id and resolution columns
    output_excel = "resolution_prompts_analysis.xlsx"
    prompt_files_folder = "individual_prompts"
    
    print("🚀 Starting Resolution Data Processing & Prompt Generation...")
    print("=" * 80)
    
    # Check if input files exist
    for file_path, file_desc in [(sheet1_file, "Sheet1"), (excel2_file, "Excel2")]:
        if not os.path.exists(file_path):
            print(f"❌ Error: {file_desc} file '{file_path}' not found!")
            print(f"Please update the file path in the script.")
            
            print(f"\n📁 Files in current directory:")
            for file in os.listdir('.'):
                if file.endswith(('.xlsx', '.xls')):
                    print(f"  - {file}")
            exit(1)
    
    # Process the data and generate prompts
    result_df = process_resolution_data_and_generate_prompts(
        sheet1_file, 
        excel2_file, 
        output_excel
    )
    
    if result_df is not None:
        # Create individual prompt files
        create_individual_prompt_files(result_df, prompt_files_folder)
        
        print("\n" + "=" * 80)
        print("🎉 PROCESSING COMPLETE!")
        print(f"📊 Main analysis: {output_excel}")
        print(f"📁 Individual prompts: {prompt_files_folder}/")
        print(f"🤖 Ready to use AI prompts for resolution generation!")
        
        print(f"\n📈 SUMMARY:")
        print(f"✅ Processed {len(result_df)} issue types")
        print(f"📋 Total resolution entries: {result_df['total_resolutions'].sum()}")
        print(f"🔍 Average resolutions per type: {result_df['total_resolutions'].mean():.1f}")
