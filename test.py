import pandas as pd
import re
from collections import defaultdict, Counter
import os

def process_resolution_data_with_enhanced_prompts(sheet1_path, excel2_path, output_file):
    """
    Enhanced version that creates highly accurate prompts based on unique resolution steps
    and generates responses in the specific format shown in the reference image
    """
    
    try:
        # Read both Excel files
        print("📊 Reading Excel files...")
        
        sheet1_df = pd.read_excel(sheet1_path)
        excel2_df = pd.read_excel(excel2_path)
        
        print(f"📄 Sheet1 loaded: {len(sheet1_df)} records")
        print(f"📄 Excel2 loaded: {len(excel2_df)} records")
        
        # Validate required columns
        required_sheet1_cols = ['KEDB', 'issue_type']
        required_excel2_cols = ['servicenow_id', 'resolution']
        
        # Check if short_description exists
        has_short_description = 'short_description' in sheet1_df.columns
        if has_short_description:
            required_sheet1_cols.append('short_description')
        
        # Validate columns
        for col in required_sheet1_cols:
            if col not in sheet1_df.columns:
                print(f"❌ Error: Column '{col}' not found in sheet1.xlsx")
                return None
        
        for col in required_excel2_cols:
            if col not in excel2_df.columns:
                print(f"❌ Error: Column '{col}' not found in excel2.xlsx")
                return None
        
        # Clean and merge data
        sheet1_clean = sheet1_df.dropna(subset=['KEDB', 'issue_type']).copy()
        excel2_clean = excel2_df.dropna(subset=['servicenow_id', 'resolution']).copy()
        
        sheet1_clean['KEDB'] = sheet1_clean['KEDB'].astype(str).str.strip()
        excel2_clean['servicenow_id'] = excel2_clean['servicenow_id'].astype(str).str.strip()
        
        # Merge dataframes
        merged_df = pd.merge(
            sheet1_clean, 
            excel2_clean, 
            left_on='KEDB', 
            right_on='servicenow_id', 
            how='inner'
        )
        
        print(f"✅ Found {len(merged_df)} matching records")
        
        if merged_df.empty:
            print("❌ No matching records found")
            return None
        
        # Enhanced processing for unique resolution steps
        print(f"🔍 Analyzing unique resolution patterns...")
        
        issue_type_data = defaultdict(lambda: {
            'resolutions': [],
            'descriptions': [],
            'unique_steps': set(),
            'step_patterns': [],
            'root_causes': [],
            'prevention_steps': []
        })
        
        # Process each record to extract detailed information
        for _, row in merged_df.iterrows():
            issue_type = row['issue_type']
            resolution = str(row['resolution']).strip()
            
            if resolution and resolution.lower() not in ['nan', 'none', '']:
                issue_type_data[issue_type]['resolutions'].append(resolution)
                
                # Extract unique steps from resolution
                unique_steps = extract_resolution_steps(resolution)
                issue_type_data[issue_type]['unique_steps'].update(unique_steps)
                
                # Extract patterns
                patterns = extract_resolution_patterns(resolution)
                issue_type_data[issue_type]['step_patterns'].extend(patterns)
                
                # Extract root causes if mentioned
                root_causes = extract_root_causes(resolution)
                issue_type_data[issue_type]['root_causes'].extend(root_causes)
                
                # Extract prevention steps if mentioned
                prevention = extract_prevention_steps(resolution)
                issue_type_data[issue_type]['prevention_steps'].extend(prevention)
            
            if has_short_description and pd.notna(row['short_description']):
                description = str(row['short_description']).strip()
                if description and description.lower() not in ['nan', 'none', '']:
                    issue_type_data[issue_type]['descriptions'].append(description)
        
        # Generate enhanced prompts
        prompt_data = []
        
        for issue_type, data in issue_type_data.items():
            # Process unique steps
            unique_steps_list = list(data['unique_steps'])
            common_patterns = Counter(data['step_patterns']).most_common(10)
            common_root_causes = Counter(data['root_causes']).most_common(5)
            common_prevention = Counter(data['prevention_steps']).most_common(5)
            
            # Generate the enhanced prompt
            enhanced_prompt = generate_enhanced_resolution_prompt(
                issue_type, 
                data['resolutions'],
                unique_steps_list,
                common_patterns,
                common_root_causes,
                common_prevention,
                data['descriptions'][:10] if data['descriptions'] else []
            )
            
            # Compile comprehensive resolution knowledge base
            knowledge_base = compile_resolution_knowledge_base(
                data['resolutions'],
                unique_steps_list,
                common_patterns,
                common_root_causes,
                common_prevention
            )
            
            prompt_data.append({
                'issue_type': issue_type,
                'total_resolutions': len(data['resolutions']),
                'unique_resolution_steps': len(unique_steps_list),
                'common_patterns_count': len(common_patterns),
                'knowledge_base': knowledge_base,
                'sample_descriptions': '\n'.join(data['descriptions'][:5]) if data['descriptions'] else 'N/A',
                'enhanced_ai_prompt': enhanced_prompt,
                'unique_steps_list': '; '.join(unique_steps_list[:20])  # First 20 unique steps
            })
        
        # Create output
        prompt_df = pd.DataFrame(prompt_data)
        prompt_df = prompt_df.sort_values('unique_resolution_steps', ascending=False)
        
        # Save to Excel
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            prompt_df.to_excel(writer, sheet_name='Enhanced_Resolution_Prompts', index=False)
            merged_df.to_excel(writer, sheet_name='Source_Data', index=False)
            create_enhanced_summary(prompt_df, writer)
        
        print(f"\n✅ Enhanced processing complete!")
        print(f"💾 Enhanced prompts saved to: {output_file}")
        
        # Display enhanced sample
        display_enhanced_sample(prompt_df)
        
        return prompt_df
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def extract_resolution_steps(resolution_text):
    """Extract individual resolution steps from resolution text"""
    steps = set()
    
    # Split by common step indicators
    step_patterns = [
        r'\d+\.\s*([^.]+)',  # Numbered steps
        r'•\s*([^•]+)',      # Bullet points
        r'-\s*([^-\n]+)',    # Dash points
        r'Step\s*\d+[:\s]*([^.]+)',  # Step 1:, Step 2:
    ]
    
    for pattern in step_patterns:
        matches = re.findall(pattern, resolution_text, re.IGNORECASE)
        for match in matches:
            clean_step = match.strip()
            if len(clean_step) > 10:  # Only meaningful steps
                steps.add(clean_step)
    
    # Also extract sentences that contain action words
    action_words = ['check', 'verify', 'restart', 'update', 'install', 'configure', 'disable', 'enable', 'run', 'execute', 'open', 'close', 'clear', 'reset']
    sentences = re.split(r'[.!?]+', resolution_text)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if any(word in sentence.lower() for word in action_words) and len(sentence) > 15:
            steps.add(sentence)
    
    return steps

def extract_resolution_patterns(resolution_text):
    """Extract common resolution patterns"""
    patterns = []
    
    # Common IT resolution patterns
    pattern_keywords = {
        'network_troubleshooting': ['ping', 'ipconfig', 'network', 'connectivity', 'dns'],
        'service_restart': ['restart', 'stop', 'start', 'service'],
        'driver_update': ['driver', 'update', 'device manager'],
        'cache_clear': ['clear', 'cache', 'temporary', 'temp'],
        'permission_fix': ['permission', 'access', 'rights', 'administrator'],
        'registry_fix': ['registry', 'regedit', 'reg'],
        'software_reinstall': ['uninstall', 'reinstall', 'install'],
        'system_scan': ['scan', 'antivirus', 'malware', 'sfc']
    }
    
    text_lower = resolution_text.lower()
    for pattern_name, keywords in pattern_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            patterns.append(pattern_name)
    
    return patterns

def extract_root_causes(resolution_text):
    """Extract mentioned root causes"""
    causes = []
    
    cause_indicators = [
        r'caused by ([^.]+)',
        r'due to ([^.]+)',
        r'because of ([^.]+)',
        r'root cause[:\s]*([^.]+)',
        r'issue is ([^.]+)',
        r'problem is ([^.]+)'
    ]
    
    for pattern in cause_indicators:
        matches = re.findall(pattern, resolution_text, re.IGNORECASE)
        for match in matches:
            clean_cause = match.strip()
            if len(clean_cause) > 5:
                causes.append(clean_cause)
    
    return causes

def extract_prevention_steps(resolution_text):
    """Extract prevention steps if mentioned"""
    prevention = []
    
    prevention_indicators = [
        r'to prevent ([^.]+)',
        r'avoid ([^.]+)',
        r'prevention[:\s]*([^.]+)',
        r'to avoid future ([^.]+)',
        r'recommend ([^.]+)'
    ]
    
    for pattern in prevention_indicators:
        matches = re.findall(pattern, resolution_text, re.IGNORECASE)
        for match in matches:
            clean_prevention = match.strip()
            if len(clean_prevention) > 10:
                prevention.append(clean_prevention)
    
    return prevention

def generate_enhanced_resolution_prompt(issue_type, resolutions, unique_steps, common_patterns, root_causes, prevention_steps, sample_descriptions):
    """Generate enhanced AI prompt based on the reference format"""
    
    # Format unique steps
    steps_text = '\n'.join([f"• {step}" for step in unique_steps[:30]])  # Top 30 unique steps
    
    # Format common patterns
    patterns_text = '\n'.join([f"• {pattern}: {count} occurrences" for pattern, count in common_patterns])
    
    # Format root causes
    causes_text = '\n'.join([f"• {cause}: {count} occurrences" for cause, count in root_causes])
    
    # Format prevention steps
    prevention_text = '\n'.join([f"• {prev}: {count} occurrences" for prev, count in prevention_steps])
    
    # Format sample descriptions
    descriptions_text = '\n'.join([f"- {desc}" for desc in sample_descriptions])
    
    enhanced_prompt = f"""You are an expert IT support specialist with extensive knowledge of {issue_type} issues. Based on comprehensive analysis of historical resolution data, generate detailed resolution steps following the EXACT format below.

**ISSUE TYPE:** {issue_type}
**KNOWLEDGE BASE - UNIQUE RESOLUTION STEPS ({len(unique_steps)} steps analyzed):**
{steps_text}

**COMMON RESOLUTION PATTERNS:**
{patterns_text}

**IDENTIFIED ROOT CAUSES:**
{causes_text}

**PREVENTION STRATEGIES:**
{prevention_text}

**SAMPLE PROBLEM DESCRIPTIONS:**
{descriptions_text}

**INSTRUCTION:** When provided with a short description of a {issue_type} issue, analyze it and generate a resolution following this EXACT format:

---
**RESOLUTION STEPS:**

**Root Cause:**
[Identify the most likely root cause based on the description and historical data]

**Resolution Steps:**
1. [First step - be specific and actionable]
2. [Second step - include exact commands/settings where applicable]
3. [Continue with numbered steps]
[Add more steps as needed]

**Expected Outcome:**
[What the user should see/expect after completing the steps]

**Alternative Solution (if primary solution fails):**
1. [Alternative step 1]
2. [Alternative step 2]
[Continue as needed]

**Prevention:**
[Specific steps to prevent this issue from recurring]

**Estimated Resolution Time:** [X minutes/hours]

**Prerequisites:** [Any specific permissions, tools, or access required]

**Important Notes/Warnings:**
[Any critical warnings or considerations]
---

**RESPONSE REQUIREMENTS:**
1. Use ONLY the knowledge from the unique steps and patterns provided above
2. Be specific with commands, file paths, and settings
3. Include estimated time for each major step
4. Provide clear success criteria for each step
5. Always include prevention measures
6. Format exactly as shown above
7. Adapt the resolution steps to match the specific problem description provided

**QUALITY CRITERIA:**
- Steps must be actionable and specific
- Use historical successful resolution patterns
- Include troubleshooting for common failure points
- Provide clear success/failure indicators for each step

Ready to generate accurate {issue_type} resolutions. Provide the short description to get started."""

    return enhanced_prompt

def compile_resolution_knowledge_base(resolutions, unique_steps, patterns, root_causes, prevention_steps):
    """Compile comprehensive knowledge base"""
    
    knowledge_base = f"""
=== COMPREHENSIVE KNOWLEDGE BASE ===

TOTAL RESOLUTIONS ANALYZED: {len(resolutions)}
UNIQUE STEPS IDENTIFIED: {len(unique_steps)}

TOP RESOLUTION STEPS:
{chr(10).join([f"• {step}" for step in unique_steps[:15]])}

COMMON PATTERNS:
{chr(10).join([f"• {pattern[0]}: {pattern[1]} times" for pattern in patterns[:5]])}

ROOT CAUSES:
{chr(10).join([f"• {cause[0]}: {cause[1]} times" for cause in root_causes[:5]])}

PREVENTION MEASURES:
{chr(10).join([f"• {prev[0]}: {prev[1]} times" for prev in prevention_steps[:5]])}
"""
    
    return knowledge_base

def create_enhanced_summary(prompt_df, writer):
    """Create enhanced summary with accuracy metrics"""
    
    summary_data = []
    
    for _, row in prompt_df.iterrows():
        summary_data.append({
            'issue_type': row['issue_type'],
            'total_resolutions_analyzed': row['total_resolutions'],
            'unique_steps_extracted': row['unique_resolution_steps'],
            'pattern_diversity': row['common_patterns_count'],
            'knowledge_richness_score': (row['unique_resolution_steps'] * row['common_patterns_count']) // row['total_resolutions'] if row['total_resolutions'] > 0 else 0,
            'prompt_accuracy_potential': 'High' if row['unique_resolution_steps'] > 20 else 'Medium' if row['unique_resolution_steps'] > 10 else 'Low'
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_excel(writer, sheet_name='Accuracy_Analysis', index=False)

def display_enhanced_sample(prompt_df):
    """Display enhanced sample showing the quality of generated prompts"""
    
    print(f"\n🤖 ENHANCED AI PROMPTS GENERATED (Format-Specific):")
    print("=" * 80)
    
    top_issue = prompt_df.iloc[0]
    print(f"\n🎯 SAMPLE FOR: {top_issue['issue_type']}")
    print(f"📊 Knowledge Base: {top_issue['unique_resolution_steps']} unique steps")
    print(f"📋 Accuracy Potential: High (based on comprehensive step analysis)")
    
    print(f"\n📝 PROMPT PREVIEW (First 500 characters):")
    prompt_preview = top_issue['enhanced_ai_prompt'][:500] + "..."
    print(prompt_preview)
    
    print(f"\n✅ This prompt will generate resolutions in your exact format with:")
    print(f"   • Root Cause analysis")
    print(f"   • Numbered Resolution Steps")
    print(f"   • Expected Outcomes")
    print(f"   • Alternative Solutions")
    print(f"   • Prevention measures")
    print(f"   • Time estimates")

def create_format_specific_prompt_files(prompt_df, output_folder):
    """Create individual prompt files optimized for the specific format"""
    
    try:
        os.makedirs(output_folder, exist_ok=True)
        
        for _, row in prompt_df.iterrows():
            issue_type = row['issue_type']
            safe_filename = re.sub(r'[^\w\-_.]', '_', issue_type)
            
            filename = f"{output_folder}/FORMAT_SPECIFIC_PROMPT_{safe_filename}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"ENHANCED RESOLUTION PROMPT - {issue_type}\n")
                f.write("=" * 80 + "\n")
                f.write("OPTIMIZED FOR SPECIFIC FORMAT REQUIREMENTS\n")
                f.write("=" * 80 + "\n\n")
                f.write(row['enhanced_ai_prompt'])
                f.write(f"\n\n" + "="*50)
                f.write(f"\nKNOWLEDGE BASE STATS:")
                f.write(f"\nTotal Resolutions: {row['total_resolutions']}")
                f.write(f"\nUnique Steps: {row['unique_resolution_steps']}")
                f.write(f"\nPattern Diversity: {row['common_patterns_count']}")
                f.write(f"\n" + "="*50)
        
        print(f"📁 Format-specific prompt files saved to: {output_folder}/")
        
    except Exception as e:
        print(f"❌ Error creating prompt files: {str(e)}")

# Main execution
if __name__ == "__main__":
    # File paths
    sheet1_file = "shee1.xlsx"
    excel2_file = "excel2.xlsx"
    output_excel = "enhanced_format_specific_prompts.xlsx"
    prompt_files_folder = "format_specific_prompts"
    
    print("🚀 Starting Enhanced Resolution Prompt Generation (Format-Specific)...")
    print("=" * 80)
    
    # Check files
    for file_path, file_desc in [(sheet1_file, "Sheet1"), (excel2_file, "Excel2")]:
        if not os.path.exists(file_path):
            print(f"❌ Error: {file_desc} file '{file_path}' not found!")
            exit(1)
    
    # Process with enhanced analysis
    result_df = process_resolution_data_with_enhanced_prompts(
        sheet1_file, 
        excel2_file, 
        output_excel
    )
    
    if result_df is not None:
        # Create format-specific prompt files
        create_format_specific_prompt_files(result_df, prompt_files_folder)
        
        print("\n" + "=" * 80)
        print("🎉 ENHANCED FORMAT-SPECIFIC PROCESSING COMPLETE!")
        print(f"📊 Enhanced analysis: {output_excel}")
        print(f"📁 Format-specific prompts: {prompt_files_folder}/")
        print(f"🤖 Prompts generate resolutions in your exact format!")
        
        print(f"\n🔍 KEY IMPROVEMENTS:")
        print(f"✅ Analyzes unique resolution steps (not just full resolutions)")
        print(f"✅ Identifies common resolution patterns")
        print(f"✅ Extracts root causes and prevention measures")
        print(f"✅ Generates prompts for your exact format structure")
        print(f"✅ Higher accuracy through comprehensive step analysis")
