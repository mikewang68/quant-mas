#!/usr/bin/env python3
"""
Search for programs that generate records with both golden_cross and technical_analysis fields
"""

import os
import sys
import logging

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def search_for_combined_programs():
    """Search for programs that might generate records with both golden_cross and technical_analysis"""
    print("Searching for programs that generate records with both golden_cross and technical_analysis...")
    
    # Get all Python files in test directory
    test_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'test')
    python_files = []
    
    for root, dirs, files in os.walk(test_dir):
        for file in files:
            if file.endswith('.py') and 'find_program_with_golden_cross_and_technical_analysis' not in file:
                python_files.append(os.path.join(root, file))
    
    print(f"Found {len(python_files)} Python files in test directory (excluding search script)")
    
    # Search for files that might call both selectors
    combined_programs = []
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check if file contains references to both selectors
                has_weekly_selector = 'weekly_selector' in content or 'WeeklyStockSelector' in content
                has_technical_selector = 'technical_selector' in content or 'TechnicalStockSelector' in content
                
                # Check if file contains references to both golden_cross and technical_analysis
                has_golden_cross = 'golden_cross' in content
                has_technical_analysis = 'technical_analysis' in content
                
                # Check if file contains update_pool_with_technical_analysis
                has_update_technical = 'update_pool_with_technical_analysis' in content
                
                if (has_weekly_selector and has_technical_selector) or (has_golden_cross and has_technical_analysis) or has_update_technical:
                    combined_programs.append({
                        'file': file_path,
                        'has_weekly_selector': has_weekly_selector,
                        'has_technical_selector': has_technical_selector,
                        'has_golden_cross': has_golden_cross,
                        'has_technical_analysis': has_technical_analysis,
                        'has_update_technical': has_update_technical
                    })
                    
        except Exception as e:
            logger.warning(f"Error reading {file_path}: {e}")
            continue
    
    print(f"\nFound {len(combined_programs)} potential combined programs:")
    for program in combined_programs:
        print(f"\nFile: {program['file']}")
        print(f"  Has weekly selector: {program['has_weekly_selector']}")
        print(f"  Has technical selector: {program['has_technical_selector']}")
        print(f"  Has golden_cross: {program['has_golden_cross']}")
        print(f"  Has technical_analysis: {program['has_technical_analysis']}")
        print(f"  Has update_technical: {program['has_update_technical']}")

if __name__ == "__main__":
    search_for_combined_programs()

