"""
Debug script for program file creation.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.program_manager import create_strategy_program_file, STRATEGIES_DIR

def debug_program_creation():
    """Debug program creation functionality."""
    print("Debugging program creation...")
    print(f"Strategies directory: {STRATEGIES_DIR}")
    print(f"Strategies directory exists: {STRATEGIES_DIR.exists()}")
    
    # Test creating a program file
    result = create_strategy_program_file("Debug Strategy", "technical")
    print(f"Program creation result: {result}")
    
    if result:
        program_path = Path(result)
        print(f"Program file exists: {program_path.exists()}")
        if program_path.exists():
            print(f"Program file content:")
            with open(program_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(content[:200] + "..." if len(content) > 200 else content)

if __name__ == "__main__":
    debug_program_creation()

