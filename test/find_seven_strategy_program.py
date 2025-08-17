#!/usr/bin/env python3
"""
Check which program generates 7 strategy labels in pool
"""

import sys
import os
import logging

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def search_for_seven_strategy_programs():
    """Search for programs that might generate 7 strategy labels"""
    print("Searching for programs that might generate 7 strategy labels...")
    
    # Get all Python files in test directory
    test_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'test')
    python_files = []
    
    for root, dirs, files in os.walk(test_dir):
        for file in files:
            if file.endswith('.py') and 'find_program_with_golden_cross_and_technical_analysis' not in file:
                python_files.append(os.path.join(root, file))
    
    print(f"Found {len(python_files)} Python files in test directory (excluding search script)")
    
    # Search for files that might generate 7 strategy labels
    seven_strategy_programs = []
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check if file contains references to 7 strategies or multiple strategies
                has_seven = '7' in content and ('strategy' in content or 'strategies' in content)
                has_multiple_strategies = 'strategies' in content and ('[' in content or 'list' in content)
                has_loop = 'for' in content and ('strategy' in content or 'strategies' in content)
                
                if has_seven or has_multiple_strategies or has_loop:
                    seven_strategy_programs.append({
                        'file': file_path,
                        'has_seven': has_seven,
                        'has_multiple_strategies': has_multiple_strategies,
                        'has_loop': has_loop
                    })
                    
        except Exception as e:
            logger.warning(f"Error reading {file_path}: {e}")
            continue
    
    print(f"\nFound {len(seven_strategy_programs)} potential programs that generate multiple strategies:")
    for program in seven_strategy_programs:
        print(f"\nFile: {program['file']}")
        print(f"  Has seven: {program['has_seven']}")
        print(f"  Has multiple strategies: {program['has_multiple_strategies']}")
        print(f"  Has loop: {program['has_loop']}")

if __name__ == "__main__":
    search_for_seven_strategy_programs()

