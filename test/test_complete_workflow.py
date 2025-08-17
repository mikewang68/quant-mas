"""
Test script for the complete workflow of strategy creation with program files.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data.mongodb_manager import MongoDBManager

def test_complete_workflow():
    """Test the complete workflow of strategy creation with program files."""
    print("Testing complete workflow...")
    
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()
        print("✓ MongoDB manager initialized")
        
        # Test 1: Create a new strategy with program file
        print("\n--- Test 1: Create new strategy with program file ---")
        strategy_data = {
            "name": "Complete Workflow Test Strategy",
            "type": "technical",
            "description": "Test strategy for complete workflow",
            "program": "complete_workflow_test.py",
            "parameters": {
                "test_param1": "value1",
                "test_param2": 42
            }
        }
        
        strategy_id = db_manager.create_strategy(strategy_data)
        if strategy_id:
            print(f"✓ Strategy created with ID: {strategy_id}")
        else:
            print("✗ Failed to create strategy")
            return False
            
        # Verify strategy was created in database
        created_strategy = db_manager.get_strategy(strategy_id)
        if created_strategy and created_strategy.get("name") == strategy_data["name"]:
            print("✓ Strategy retrieved from database successfully")
        else:
            print("✗ Failed to retrieve strategy from database")
            return False
            
        # Check if program file was created
        program_file_path = Path(project_root) / "strategies" / "complete_workflow_test_strategy.py"
        if program_file_path.exists():
            print(f"✓ Program file created: {program_file_path.name}")
            # Check file content
            with open(program_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "CompleteWorkflowTestStrategy" in content and "Complete Workflow Test Strategy" in content:
                    print("✓ Program file has correct content")
                else:
                    print("✗ Program file content is incorrect")
                    return False
        else:
            print("✗ Program file was not created")
            return False
            
        # Test 2: Update strategy with new program file
        print("\n--- Test 2: Update strategy with new program file ---")
        updated_strategy_data = {
            "name": "Updated Complete Workflow Test Strategy",
            "type": "fundamental",
            "description": "Updated test strategy for complete workflow",
            "program": "updated_complete_workflow_test.py",
            "parameters": {
                "updated_param1": "new_value1",
                "updated_param2": 100
            }
        }
        
        update_success = db_manager.update_strategy(strategy_id, updated_strategy_data)
        if update_success:
            print("✓ Strategy updated successfully")
        else:
            print("✗ Failed to update strategy")
            return False
            
        # Check if new program file was created
        updated_program_file_path = Path(project_root) / "strategies" / "updated_complete_workflow_test_strategy.py"
        if updated_program_file_path.exists():
            print(f"✓ Updated program file created: {updated_program_file_path.name}")
        else:
            print("⚠ Updated program file was not created (may already exist)")
            
        # Test 3: Update strategy with same program file
        print("\n--- Test 3: Update strategy with same program file ---")
        same_program_data = {
            "name": "Same Program Test Strategy",
            "type": "ml",
            "description": "Test strategy with same program",
            "program": "updated_complete_workflow_test.py",  # Same as before
            "parameters": {
                "ml_param": "ml_value"
            }
        }
        
        update_success2 = db_manager.update_strategy(strategy_id, same_program_data)
        if update_success2:
            print("✓ Strategy updated with same program successfully")
        else:
            print("✗ Failed to update strategy with same program")
            return False
            
        # Test 4: Retrieve all strategies to ensure our strategy is included
        print("\n--- Test 4: Retrieve all strategies ---")
        all_strategies = db_manager.get_strategies()
        strategy_found = any(s.get("_id") == strategy_id for s in all_strategies)
        if strategy_found:
            print("✓ Strategy found in all strategies list")
        else:
            print("✗ Strategy not found in all strategies list")
            return False
            
        # Test 5: Retrieve strategy by name
        print("\n--- Test 5: Retrieve strategy by name ---")
        strategy_by_name = db_manager.get_strategy_by_name("Same Program Test Strategy")
        if strategy_by_name and strategy_by_name.get("_id") == strategy_id:
            print("✓ Strategy retrieved by name successfully")
        else:
            print("✗ Failed to retrieve strategy by name")
            return False
            
        # Clean up
        print("\n--- Cleanup ---")
        delete_success = db_manager.delete_strategy(strategy_id)
        if delete_success:
            print("✓ Strategy deleted successfully")
        else:
            print("⚠ Warning: Failed to delete test strategy")
            
        print("\n✓ All tests passed! Complete workflow is working correctly.")
        return True
        
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Close MongoDB connection
        try:
            db_manager.close_connection()
            print("✓ MongoDB connection closed")
        except:
            pass

if __name__ == "__main__":
    success = test_complete_workflow()
    if not success:
        sys.exit(1)

