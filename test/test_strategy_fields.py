#!/usr/bin/env python3
"""
Test script to verify that the MongoDBManager handles the new file and class_name fields properly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

def test_strategy_fields():
    """Test that strategies are handled with new fields properly"""
    try:
        # Initialize MongoDB manager
        manager = MongoDBManager()

        # Test creating a strategy with new fields
        test_strategy = {
            "name": "Test Strategy",
            "type": "technical",
            "description": "Test strategy for field handling",
            "file": "test_strategy_file",
            "class_name": "TestStrategyClass",
            "parameters": {"param1": "value1"}
        }

        # Create strategy
        strategy_id = manager.create_strategy(test_strategy)
        print(f"Created strategy with ID: {strategy_id}")

        if not strategy_id:
            print("Failed to create strategy")
            return False

        # Get all strategies
        strategies = manager.get_strategies()
        print(f"Found {len(strategies)} strategies")

        # Find our test strategy
        test_strategy_found = None
        for strategy in strategies:
            if strategy.get('_id') == strategy_id:
                test_strategy_found = strategy
                break

        if not test_strategy_found:
            print("Failed to find test strategy")
            return False

        # Check that fields are present
        if 'file' not in test_strategy_found:
            print("File field not found in strategy")
            return False

        if 'class_name' not in test_strategy_found:
            print("Class name field not found in strategy")
            return False

        print("Test strategy fields:")
        print(f"  File: {test_strategy_found['file']}")
        print(f"  Class name: {test_strategy_found['class_name']}")

        # Test getting specific strategy
        specific_strategy = manager.get_strategy(strategy_id)
        if not specific_strategy:
            print("Failed to get specific strategy")
            return False

        if 'file' not in specific_strategy:
            print("File field not found in specific strategy")
            return False

        if 'class_name' not in specific_strategy:
            print("Class name field not found in specific strategy")
            return False

        print("Specific strategy fields:")
        print(f"  File: {specific_strategy['file']}")
        print(f"  Class name: {specific_strategy['class_name']}")

        # Test updating strategy
        update_data = {
            "name": "Updated Test Strategy",
            "file": "updated_test_strategy_file",
            "class_name": "UpdatedTestStrategyClass"
        }

        success = manager.update_strategy(strategy_id, update_data)
        if not success:
            print("Failed to update strategy")
            return False

        # Check updated strategy
        updated_strategy = manager.get_strategy(strategy_id)
        if not updated_strategy:
            print("Failed to get updated strategy")
            return False

        if updated_strategy.get('name') != "Updated Test Strategy":
            print("Strategy name not updated")
            return False

        if updated_strategy.get('file') != "updated_test_strategy_file":
            print("Strategy file not updated")
            return False

        if updated_strategy.get('class_name') != "UpdatedTestStrategyClass":
            print("Strategy class name not updated")
            return False

        print("Strategy updated successfully")

        # Test backward compatibility with program field
        legacy_strategy = {
            "name": "Legacy Strategy",
            "type": "technical",
            "description": "Legacy strategy with program field",
            "program": {"file": "legacy_file", "class": "LegacyClass"},
            "parameters": {}
        }

        legacy_strategy_id = manager.create_strategy(legacy_strategy)
        if not legacy_strategy_id:
            print("Failed to create legacy strategy")
            return False

        # Get legacy strategy and check field mapping
        retrieved_legacy = manager.get_strategy(legacy_strategy_id)
        if not retrieved_legacy:
            print("Failed to retrieve legacy strategy")
            return False

        # Check that program field is mapped to file/class_name
        if retrieved_legacy.get('file') != "legacy_file":
            print("Legacy program file not mapped correctly")
            return False

        if retrieved_legacy.get('class_name') != "LegacyClass":
            print("Legacy program class not mapped correctly")
            return False

        print("Backward compatibility test passed")

        # Cleanup
        manager.delete_strategy(strategy_id)
        manager.delete_strategy(legacy_strategy_id)

        print("All tests passed!")
        return True

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            manager.close_connection()
        except:
            pass

if __name__ == "__main__":
    success = test_strategy_fields()
    if not success:
        sys.exit(1)

