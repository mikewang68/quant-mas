"""
Debug script for MongoDB program creation integration.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data.mongodb_manager import MongoDBManager

def debug_mongodb_program():
    """Debug MongoDB program creation."""
    print("Debugging MongoDB program creation...")
    
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()
        print("✓ MongoDB manager initialized")
        
        # Test the program creation function directly
        from utils.program_manager import create_strategy_program_file
        result = create_strategy_program_file("Direct Test Strategy", "technical")
        print(f"Direct program creation result: {result}")
        
        # Create a test strategy
        test_strategy = {
            "name": "Test Strategy",
            "type": "technical",
            "description": "Test strategy",
            "program": "test_strategy.py",
            "parameters": {}
        }
        
        print("Creating strategy with program field...")
        strategy_id = db_manager.create_strategy(test_strategy)
        print(f"Strategy ID: {strategy_id}")
        
        # Check if program file was created
        program_path = Path(project_root) / "strategies" / "test_strategy.py"
        print(f"Program file path: {program_path}")
        print(f"Program file exists: {program_path.exists()}")
        
        if program_path.exists():
            print("✓ Program file was created successfully")
        else:
            print("✗ Program file was not created")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_mongodb_program()

