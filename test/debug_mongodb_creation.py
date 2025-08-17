"""
Debug script for MongoDB strategy creation with program file.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Enable logging to see what's happening
import logging
logging.basicConfig(level=logging.DEBUG)

from data.mongodb_manager import MongoDBManager

def debug_mongodb_creation():
    """Debug MongoDB strategy creation with program file."""
    print("Debugging MongoDB strategy creation...")
    
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()
        print("✓ MongoDB manager initialized")
        
        # Test the program creation function directly first
        print("Testing program creation function directly...")
        from utils.program_manager import create_strategy_program_file
        direct_result = create_strategy_program_file("Direct Test Strategy", "technical")
        print(f"Direct program creation result: {direct_result}")
        if direct_result:
            direct_path = Path(direct_result)
            print(f"Direct program file exists: {direct_path.exists()}")
        
        # Create a test strategy with program field
        test_strategy = {
            "name": "Debug MongoDB Strategy",
            "type": "technical",
            "description": "Debug strategy for MongoDB integration",
            "program": "debug_mongodb_strategy.py",  # This will become debug_mongodb_strategy_strategy.py
            "parameters": {
                "test_param": "test_value"
            }
        }
        
        print(f"Creating strategy with data: {test_strategy}")
        
        # Create the strategy
        strategy_id = db_manager.create_strategy(test_strategy)
        print(f"Strategy creation result - ID: {strategy_id}")
        
        if strategy_id:
            print("✓ Strategy created successfully in database")
            
            # Check if program file was created (note: program manager adds _strategy.py suffix)
            program_file_path = Path(project_root) / "strategies" / "debug_mongodb_strategy_strategy.py"
            print(f"Checking for program file: {program_file_path}")
            print(f"Program file exists: {program_file_path.exists()}")
            
            if program_file_path.exists():
                print("✓ Program file created successfully")
                # Read and display first part of the file
                with open(program_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"Program file content preview: {content[:100]}...")
            else:
                print("✗ Program file was not created")
                # List files in strategies directory to see what's there
                strategies_dir = Path(project_root) / "strategies"
                if strategies_dir.exists():
                    print("Files in strategies directory:")
                    for f in strategies_dir.iterdir():
                        if f.is_file() and f.name.endswith('.py') and 'debug_mongodb' in f.name:
                            print(f"  {f.name}")
                
            # Clean up
            try:
                db_manager.delete_strategy(strategy_id)
                print("✓ Test strategy cleaned up")
            except Exception as e:
                print(f"⚠ Warning: Failed to clean up test strategy: {e}")
        else:
            print("✗ Failed to create strategy in database")
            
    except Exception as e:
        print(f"✗ Error during debugging: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close MongoDB connection
        try:
            db_manager.close_connection()
            print("✓ MongoDB connection closed")
        except:
            pass

if __name__ == "__main__":
    debug_mongodb_creation()

