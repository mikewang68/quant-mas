"""
Test script for program file creation functionality.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.program_manager import create_strategy_program_file

def test_program_creation():
    """Test the program creation functionality."""
    print("Testing program file creation...")
    
    # Test creating a technical strategy
    result = create_strategy_program_file("Test Moving Average Strategy", "technical")
    if result:
        print(f"✓ Created technical strategy program: {result}")
    else:
        print("✗ Failed to create technical strategy program")
        
    # Test creating a fundamental strategy
    result = create_strategy_program_file("Test Fundamental Strategy", "fundamental")
    if result:
        print(f"✓ Created fundamental strategy program: {result}")
    else:
        print("✗ Failed to create fundamental strategy program")
        
    # Test creating an ML strategy
    result = create_strategy_program_file("Test Machine Learning Strategy", "ml")
    if result:
        print(f"✓ Created ML strategy program: {result}")
    else:
        print("✗ Failed to create ML strategy program")
        
    # Test creating a strategy with special characters
    result = create_strategy_program_file("Test Strategy with Special Characters!", "technical")
    if result:
        print(f"✓ Created strategy with special characters: {result}")
    else:
        print("✗ Failed to create strategy with special characters")

if __name__ == "__main__":
    test_program_creation()

