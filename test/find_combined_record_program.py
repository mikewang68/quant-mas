#!/usr/bin/env python3
"""
Find which program generates records with both golden_cross and technical_analysis
"""

import os
import sys
import logging

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def search_for_combined_record_programs():
    """Search for programs that generate records with both golden_cross and technical_analysis"""
    print("Searching for programs that generate records with both golden_cross and technical_analysis...")
    
    # Get all Python files in test directory
    test_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'test')
    python_files = []
    
    for root, dirs, files in os.walk(test_dir):
        for file in files:
            if file.endswith('.py') and 'find_program_with_golden_cross_and_technical_analysis' not in file:
                python_files.append(os.path.join(root, file))
    
    print(f"Found {len(python_files)} Python files in test directory (excluding search script)")
    
    # Search for files that might generate combined records
    combined_programs = []
    
    keywords = [
        'golden_cross', 'technical_analysis', 
        'update_pool_with_technical_analysis',
        'weekly.*technical', 'technical.*weekly'
    ]
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for specific patterns
                has_golden_cross = 'golden_cross' in content
                has_technical_analysis = 'technical_analysis' in content
                has_update_method = 'update_pool_with_technical_analysis' in content
                has_weekly_and_technical = ('weekly_selector' in content and 'technical_selector' in content)
                
                # Check if file imports both selectors
                has_weekly_import = 'from agents.weekly_selector import' in content or 'import.*weekly_selector' in content
                has_technical_import = 'from agents.technical_selector import' in content or 'import.*technical_selector' in content
                
                # Check for specific method calls
                calls_both_selectors = ('WeeklyStockSelector(' in content and 'TechnicalStockSelector(' in content)
                
                if (has_golden_cross and has_technical_analysis) or has_update_method or (has_weekly_and_technical and has_weekly_import and has_technical_import) or calls_both_selectors:
                    combined_programs.append({
                        'file': os.path.basename(file_path),
                        'path': file_path,
                        'has_golden_cross': has_golden_cross,
                        'has_technical_analysis': has_technical_analysis,
                        'has_update_method': has_update_method,
                        'has_weekly_and_technical': has_weekly_and_technical,
                        'has_weekly_import': has_weekly_import,
                        'has_technical_import': has_technical_import,
                        'calls_both_selectors': calls_both_selectors
                    })
                    
        except Exception as e:
            logger.warning(f"Error reading {file_path}: {e}")
            continue
    
    print(f"\nFound {len(combined_programs)} potential programs that generate combined records:")
    for program in combined_programs:
        print(f"\nFile: {program['file']}")
        print(f"  Path: {program['path']}")
        print(f"  Has golden_cross: {program['has_golden_cross']}")
        print(f"  Has technical_analysis: {program['has_technical_analysis']}")
        print(f"  Has update method: {program['has_update_method']}")
        print(f"  Has weekly and technical: {program['has_weekly_and_technical']}")
        print(f"  Has weekly import: {program['has_weekly_import']}")
        print(f"  Has technical import: {program['has_technical_import']}")
        print(f"  Calls both selectors: {program['calls_both_selectors']}")

if __name__ == "__main__":
    search_for_combined_record_programs()

