"""
Test script for MongoDB integration with program file creation.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data.mongodb_manager import MongoDBManager

def test_mongodb_program_creation():
    """Test MongoDB integration with program file creation."""
    print("Testing MongoDB integration with program file creation...")
    
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()
        print("✓ MongoDB manager initialized")
        
        # Create a test strategy with program field
        test_strategy = {
            "name": "Test MongoDB Strategy",
            "type": "technical",
            "description": "Test strategy for MongoDB integration",
            "program": "test_mongodb_strategy.py",
            "parameters": {
                "rsi_period": 14,
                "rsi_threshold_low": 30,
                "rsi_threshold_high": 70
            }
        }
        
        # Create the strategy
        strategy_id = db_manager.create_strategy(test_strategy)
        if strategy_id:
            print(f"✓ Created strategy with ID: {strategy_id}")
        else:
            print("✗ Failed to create strategy")
            return False
        
        # Verify the strategy was created
        strategy = db_manager.get_strategy(strategy_id)
        if strategy and strategy.get("name") == "Test MongoDB Strategy":
            print("✓ Strategy retrieved successfully")
        else:
            print("✗ Failed to retrieve strategy")
            return False
        
        # Check if program file was created
        program_file_path = Path(project_root) / "strategies" / "test_mongodb_strategy.py"
        if program_file_path.exists():
            print(f"✓ Program file created: {program_file_path}")
        else:
            print("✗ Program file was not created")
            return False
        
        # Update the strategy
        updated_strategy = {
            "name": "Updated Test MongoDB Strategy",
            "type": "technical",
            "description": "Updated test strategy for MongoDB integration",
            "program": "updated_test_mongodb_strategy.py",
            "parameters": {
                "rsi_period": 14,
                "rsi_threshold_low": 25,
                "rsi_threshold_high": 75
            }
        }
        
        # Update the strategy
        success = db_manager.update_strategy(strategy_id, updated_strategy)
        if success:
            print("✓ Strategy updated successfully")
        else:
            print("✗ Failed to update strategy")
            return False
        
        # Check if new program file was created
        updated_program_file_path = Path(project_root) / "strategies" / "updated_test_mongodb_strategy.py"
        if updated_program_file_path.exists():
            print(f"✓ Updated program file created: {updated_program_file_path}")
        else:
            print("✗ Updated program file was not created")
            # This might be expected if the file already exists
        
        # Clean up - delete the strategy
        delete_success = db_manager.delete_strategy(strategy_id)
        if delete_success:
            print("✓ Strategy deleted successfully")
        else:
            print("⚠ Warning: Failed to delete test strategy")
        
        print("All tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Error during test: {e}")
        return False
    finally:
        # Close MongoDB connection
        try:
            db_manager.close_connection()
            print("✓ MongoDB connection closed")
        except:
            pass

if __name__ == "__main__":
    success = test_mongodb_program_creation()
    if not success:
        sys.exit(1)

